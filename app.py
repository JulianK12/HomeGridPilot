from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import json
from datetime import datetime, timedelta
import random
import time
from functools import wraps

app = Flask(__name__)
app.secret_key = "shelly-dashboard-secret-2024"

# ─────────────────────────────────────────────
# In-memory storage (replace with a DB in prod)
# ─────────────────────────────────────────────
USERS = {
    "admin": "admin123"
}

devices = {}          # id -> device config
power_history = {}    # id -> list of {ts, watt}

# ─── Auth helper ──────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────────
# Pages
# ─────────────────────────────────────────────
@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login_page"))
    return render_template("dashboard.html")

@app.route("/login")
def login_page():
    if session.get("logged_in"):
        return redirect(url_for("index"))
    return render_template("login.html")

# ─────────────────────────────────────────────
# Auth API
# ─────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")
    if USERS.get(username) == password:
        session["logged_in"] = True
        session["username"] = username
        return jsonify({"ok": True, "username": username})
    return jsonify({"ok": False, "error": "Ungültiger Benutzername oder Passwort"}), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/me")
def me():
    if session.get("logged_in"):
        return jsonify({"logged_in": True, "username": session.get("username")})
    return jsonify({"logged_in": False})

# ─────────────────────────────────────────────
# Device Management
# ─────────────────────────────────────────────
@app.route("/api/devices", methods=["GET"])
@login_required
def get_devices():
    return jsonify(list(devices.values()))

@app.route("/api/devices", methods=["POST"])
@login_required
def add_device():
    data = request.get_json()
    device_id = f"dev_{int(time.time()*1000)}"
    ip = data.get("ip", "").strip()
    name = data.get("name", "Shelly Gerät").strip()
    device_type = data.get("type", "plug")

    if not ip:
        return jsonify({"error": "IP-Adresse erforderlich"}), 400

    device = {
        "id": device_id,
        "name": name,
        "ip": ip,
        "type": device_type,
        "online": False,
        "relay_on": False,
        "power_w": 0.0,
        "voltage_v": 0.0,
        "current_a": 0.0,
        "energy_kwh": 0.0,
        "added": datetime.now().isoformat()
    }
    devices[device_id] = device
    power_history[device_id] = []
    return jsonify(device), 201

@app.route("/api/devices/<device_id>", methods=["DELETE"])
@login_required
def delete_device(device_id):
    if device_id in devices:
        del devices[device_id]
        power_history.pop(device_id, None)
        return jsonify({"ok": True})
    return jsonify({"error": "Nicht gefunden"}), 404

# ─────────────────────────────────────────────
# Live Device Status  (real Shelly HTTP API)
# ─────────────────────────────────────────────
def fetch_shelly_status(device):
    ip = device["ip"]
    try:
        # Gen1 style
        r = requests.get(f"http://{ip}/status", timeout=3)
        if r.status_code == 200:
            s = r.json()
            meters = s.get("meters", [{}])
            emeters = s.get("emeters", [{}])
            relays = s.get("relays", [{}])
            m = meters[0] if meters else {}
            em = emeters[0] if emeters else {}

            power = m.get("power", em.get("power", 0.0))
            voltage = em.get("voltage", s.get("voltage", 0.0))
            current = em.get("current", 0.0)
            total_energy = m.get("total", em.get("total", 0.0)) / 1000.0  # Wh→kWh
            relay_on = relays[0].get("ison", False) if relays else False

            return {
                "online": True,
                "relay_on": relay_on,
                "power_w": round(power, 2),
                "voltage_v": round(voltage, 1),
                "current_a": round(current, 3),
                "energy_kwh": round(total_energy, 4),
            }
    except Exception:
        pass

    # Try Gen2/Gen3 RPC
    try:
        r = requests.post(
            f"http://{ip}/rpc/Switch.GetStatus",
            json={"id": 0}, timeout=3
        )
        if r.status_code == 200:
            s = r.json()
            apower = s.get("apower", 0.0)
            voltage = s.get("voltage", 0.0)
            current = s.get("current", 0.0)
            energy = s.get("aenergy", {}).get("total", 0.0) / 1000.0
            relay_on = s.get("output", False)
            return {
                "online": True,
                "relay_on": relay_on,
                "power_w": round(apower, 2),
                "voltage_v": round(voltage, 1),
                "current_a": round(current, 3),
                "energy_kwh": round(energy, 4),
            }
    except Exception:
        pass

    return {"online": False, "relay_on": False, "power_w": 0, "voltage_v": 0, "current_a": 0, "energy_kwh": 0}


@app.route("/api/devices/<device_id>/status")
@login_required
def device_status(device_id):
    if device_id not in devices:
        return jsonify({"error": "Nicht gefunden"}), 404

    device = devices[device_id]
    status = fetch_shelly_status(device)
    device.update(status)

    # Store power history (keep last 60 entries)
    history = power_history.setdefault(device_id, [])
    history.append({"ts": datetime.now().isoformat(), "watt": status["power_w"]})
    if len(history) > 60:
        history.pop(0)

    return jsonify(device)

# ─────────────────────────────────────────────
# Relay Control
# ─────────────────────────────────────────────
def control_relay_gen1(ip, turn_on):
    action = "on" if turn_on else "off"
    r = requests.get(f"http://{ip}/relay/0?turn={action}", timeout=3)
    return r.status_code == 200

def control_relay_gen2(ip, turn_on):
    r = requests.post(
        f"http://{ip}/rpc/Switch.Set",
        json={"id": 0, "on": turn_on}, timeout=3
    )
    return r.status_code == 200

@app.route("/api/devices/<device_id>/relay", methods=["POST"])
@login_required
def set_relay(device_id):
    if device_id not in devices:
        return jsonify({"error": "Nicht gefunden"}), 404

    data = request.get_json()
    turn_on = bool(data.get("on", False))
    device = devices[device_id]
    ip = device["ip"]

    success = False
    try:
        success = control_relay_gen1(ip, turn_on)
    except Exception:
        pass

    if not success:
        try:
            success = control_relay_gen2(ip, turn_on)
        except Exception:
            pass

    if success:
        device["relay_on"] = turn_on
        return jsonify({"ok": True, "relay_on": turn_on})
    return jsonify({"ok": False, "error": "Gerät nicht erreichbar"}), 503

# ─────────────────────────────────────────────
# Power History
# ─────────────────────────────────────────────
@app.route("/api/devices/<device_id>/history")
@login_required
def device_history(device_id):
    history = power_history.get(device_id, [])
    return jsonify(history)

# ─────────────────────────────────────────────
# Demo mode: populate fake data for testing
# ─────────────────────────────────────────────
@app.route("/api/demo", methods=["POST"])
@login_required
def add_demo():
    demo_devices = [
        {"name": "Wohnzimmer Lampe", "ip": "192.168.1.100", "type": "plug"},
        {"name": "Büro PC", "ip": "192.168.1.101", "type": "plug"},
        {"name": "Kühlschrank", "ip": "192.168.1.102", "type": "plug"},
    ]
    demo_powers = [12.5, 145.0, 80.3]
    added = []
    for i, d in enumerate(demo_devices):
        device_id = f"demo_{i}"
        if device_id not in devices:
            device = {
                "id": device_id,
                "name": d["name"],
                "ip": d["ip"],
                "type": d["type"],
                "online": True,
                "relay_on": i % 2 == 0,
                "power_w": demo_powers[i],
                "voltage_v": 230.0,
                "current_a": round(demo_powers[i] / 230.0, 3),
                "energy_kwh": round(demo_powers[i] * 24 / 1000, 2),
                "added": datetime.now().isoformat(),
                "_demo": True
            }
            devices[device_id] = device
            # Generate fake history
            hist = []
            base = demo_powers[i]
            for m in range(60):
                ts = (datetime.now() - timedelta(minutes=60 - m)).isoformat()
                hist.append({"ts": ts, "watt": round(base + random.uniform(-base * 0.2, base * 0.2), 1)})
            power_history[device_id] = hist
            added.append(device)
    return jsonify({"added": len(added)})

if __name__ == "__main__":
    print("🔌 Shelly Dashboard läuft auf http://localhost:5000")
    app.run(debug=True, port=5000)
