from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import json
from datetime import datetime, timedelta
import random
import time
import os
import threading
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

# ─── Dynamische Strompreise (aWattar DE) ──────
PRICE_CACHE = {"data": [], "fetched_at": 0}

# ─── Automatisierung ──────────────────────────
AUTOMATION = {
    "enabled": False,
    "interval_sec": 300,
    "price_markup_ct": 0.0,
}
automation_log = []   # most recent first, capped at 50
_automation_thread = None

def default_automation_config():
    return {
        "enabled": False,
        "logic": "OR",            # "AND" oder "OR" - Verknüpfung der aktiven Bedingungen
        "price_enabled": False,
        "price_max_ct": 15.0,      # Einschalten, wenn Strompreis <= X ct/kWh
        "pv_enabled": False,
        "pv_min_surplus_w": 200,   # Einschalten, wenn PV-Überschuss >= X W
        "priority": 10,            # niedriger = wird bei PV-Überschuss zuerst bedient
    }

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
        "added": datetime.now().isoformat(),
        "automation": default_automation_config(),
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

def apply_relay(device, turn_on):
    """Schaltet das Relais eines Geräts (Gen1 oder Gen2/3) und aktualisiert dessen Status."""
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
    return success

@app.route("/api/devices/<device_id>/relay", methods=["POST"])
@login_required
def set_relay(device_id):
    if device_id not in devices:
        return jsonify({"error": "Nicht gefunden"}), 404

    data = request.get_json()
    turn_on = bool(data.get("on", False))
    device = devices[device_id]

    if apply_relay(device, turn_on):
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
# Dynamische Strompreise (aWattar Day-Ahead, DE)
# ─────────────────────────────────────────────
AWATTAR_URL = "https://api.awattar.de/v1/marketdata"

def fetch_awattar_prices():
    """Lädt die aktuellen Day-Ahead-Preise von aWattar und füllt den Cache."""
    try:
        r = requests.get(AWATTAR_URL, timeout=5)
        if r.status_code == 200:
            raw = r.json().get("data", [])
            PRICE_CACHE["data"] = [
                {
                    "start": item["start_timestamp"],
                    "end": item["end_timestamp"],
                    # Eur/MWh -> ct/kWh
                    "price_ct": round(item["marketprice"] / 10.0, 2),
                }
                for item in raw
            ]
            PRICE_CACHE["fetched_at"] = time.time()
    except Exception:
        pass

def get_price_data():
    """Liefert den aktuellen Strompreis sowie den Tagesverlauf (ct/kWh)."""
    if not PRICE_CACHE["data"] or time.time() - PRICE_CACHE.get("fetched_at", 0) > 1800:
        fetch_awattar_prices()

    now_ms = int(time.time() * 1000)
    today_date = datetime.now().date()
    current_price = None
    today_entries = []

    for item in PRICE_CACHE["data"]:
        start_dt = datetime.fromtimestamp(item["start"] / 1000)
        is_current = item["start"] <= now_ms < item["end"]
        if is_current:
            current_price = item["price_ct"]
        if start_dt.date() == today_date:
            today_entries.append({
                "hour": start_dt.strftime("%H:%M"),
                "price_ct": item["price_ct"],
                "is_current": is_current,
            })

    markup = AUTOMATION.get("price_markup_ct", 0.0)
    effective = round(current_price + markup, 2) if current_price is not None else None

    return {
        "current_ct_per_kwh": current_price,
        "markup_ct": markup,
        "effective_ct_per_kwh": effective,
        "unit": "ct/kWh",
        "today": today_entries,
        "source": "aWattar Day-Ahead (api.awattar.de)",
    }

@app.route("/api/price")
@login_required
def price():
    return jsonify(get_price_data())

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
        {"name": "PV-Wechselrichter", "ip": "192.168.1.103", "type": "pv"},
    ]
    demo_powers = [12.5, 145.0, 80.3, 1850.0]
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
                "_demo": True,
                "automation": default_automation_config(),
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

# ─────────────────────────────────────────────
# Automatisierung: Konfiguration
# ─────────────────────────────────────────────
@app.route("/api/devices/<device_id>/automation", methods=["POST"])
@login_required
def set_device_automation(device_id):
    if device_id not in devices:
        return jsonify({"error": "Nicht gefunden"}), 404

    data = request.get_json() or {}
    auto = devices[device_id].setdefault("automation", default_automation_config())

    auto["enabled"]          = bool(data.get("enabled", auto["enabled"]))
    auto["logic"]            = "AND" if data.get("logic", auto["logic"]) == "AND" else "OR"
    auto["price_enabled"]    = bool(data.get("price_enabled", auto["price_enabled"]))
    auto["price_max_ct"]     = float(data.get("price_max_ct", auto["price_max_ct"]))
    auto["pv_enabled"]       = bool(data.get("pv_enabled", auto["pv_enabled"]))
    auto["pv_min_surplus_w"] = float(data.get("pv_min_surplus_w", auto["pv_min_surplus_w"]))
    auto["priority"]         = int(data.get("priority", auto["priority"]))

    return jsonify({"ok": True, "automation": auto})

@app.route("/api/automation/settings", methods=["GET"])
@login_required
def get_automation_settings():
    return jsonify(AUTOMATION)

@app.route("/api/automation/settings", methods=["POST"])
@login_required
def update_automation_settings():
    data = request.get_json() or {}
    if "enabled" in data:
        AUTOMATION["enabled"] = bool(data["enabled"])
    if "interval_sec" in data:
        AUTOMATION["interval_sec"] = max(60, int(data["interval_sec"]))
    if "price_markup_ct" in data:
        AUTOMATION["price_markup_ct"] = float(data["price_markup_ct"])
    return jsonify({"ok": True, "settings": AUTOMATION})

@app.route("/api/automation/log")
@login_required
def get_automation_log():
    return jsonify(automation_log[:50])

@app.route("/api/automation/run", methods=["POST"])
@login_required
def run_automation_now():
    run_automation_cycle()
    return jsonify({"ok": True, "log": automation_log[:50]})

# ─────────────────────────────────────────────
# Automatisierung: Engine
# ─────────────────────────────────────────────
def log_automation(device_name, action, reason):
    automation_log.insert(0, {
        "ts": datetime.now().isoformat(),
        "device": device_name,
        "action": action,   # "ein" | "aus" | "fehler"
        "reason": reason,
    })
    del automation_log[50:]

def run_automation_cycle():
    """Liest Strompreis & PV-Erzeugung, schaltet Geräte gemäß ihrer Regeln."""
    price_data = get_price_data()
    current_price = price_data["effective_ct_per_kwh"]

    # PV-Erzeugung aller PV-Geräte aktualisieren und summieren
    pv_total = 0.0
    for dev in devices.values():
        if dev.get("type") == "pv":
            status = fetch_shelly_status(dev)
            dev.update(status)
            if dev.get("online"):
                pv_total += dev.get("power_w", 0.0)

    # Automatisierte Verbraucher nach Priorität (niedrig = zuerst) sortieren
    candidates = [
        d for d in devices.values()
        if d.get("type") != "pv" and d.get("automation", {}).get("enabled")
    ]
    candidates.sort(key=lambda d: d.get("automation", {}).get("priority", 10))

    remaining_pv = pv_total

    for dev in candidates:
        auto = dev["automation"]
        conditions = []
        price_ok = None
        pv_ok = None

        if auto.get("price_enabled") and current_price is not None:
            price_ok = current_price <= auto.get("price_max_ct", 0)
            conditions.append(price_ok)

        if auto.get("pv_enabled"):
            needed = auto.get("pv_min_surplus_w", 0)
            pv_ok = remaining_pv >= needed
            conditions.append(pv_ok)

        if not conditions:
            continue  # keine aktive Regel für dieses Gerät

        logic = auto.get("logic", "OR")
        target = all(conditions) if logic == "AND" else any(conditions)

        # PV-Budget reservieren, wenn dieses Gerät dadurch (mit)versorgt wird
        if target and auto.get("pv_enabled"):
            remaining_pv -= auto.get("pv_min_surplus_w", 0)

        if dev.get("relay_on") != target:
            if apply_relay(dev, target):
                parts = []
                if price_ok is not None:
                    parts.append(
                        f"Preis {current_price:.2f} ct/kWh "
                        f"{'≤' if price_ok else '>'} {auto.get('price_max_ct', 0):.2f} ct/kWh"
                    )
                if pv_ok is not None:
                    parts.append(
                        f"PV-Überschuss {pv_total:.0f} W "
                        f"{'≥' if pv_ok else '<'} {auto.get('pv_min_surplus_w', 0):.0f} W"
                    )
                joiner = " UND " if logic == "AND" and len(parts) > 1 else " ODER "
                log_automation(dev["name"], "ein" if target else "aus", joiner.join(parts))
            else:
                log_automation(dev["name"], "fehler", "Gerät nicht erreichbar")

def start_automation_thread():
    global _automation_thread
    if _automation_thread is not None:
        return

    def loop():
        while True:
            try:
                if AUTOMATION.get("enabled"):
                    run_automation_cycle()
            except Exception as e:
                log_automation("System", "fehler", str(e))
            time.sleep(max(60, AUTOMATION.get("interval_sec", 300)))

    _automation_thread = threading.Thread(target=loop, daemon=True)
    _automation_thread.start()

if __name__ == "__main__":
    # Im Debug-Modus mit Reloader läuft der Thread nur im tatsächlich
    # bedienenden Worker-Prozess (WERKZEUG_RUN_MAIN == "true"), damit
    # er den gleichen Speicherzustand (devices, etc.) sieht.
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        start_automation_thread()
    print("🔌 Shelly Dashboard läuft auf http://localhost:5000")
    app.run(debug=True, port=5000)
