"""Interface for Shelly devices (Gen1 /status + /relay, Gen2/Gen3 RPC)."""

import requests

OFFLINE_STATUS = {
    "online": False, "relay_on": False,
    "power_w": 0, "voltage_v": 0, "current_a": 0, "energy_kwh": 0,
}


def fetch_status(device):
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

    return dict(OFFLINE_STATUS)


def _set_relay_gen1(ip, turn_on):
    action = "on" if turn_on else "off"
    r = requests.get(f"http://{ip}/relay/0?turn={action}", timeout=3)
    return r.status_code == 200


def _set_relay_gen2(ip, turn_on):
    r = requests.post(
        f"http://{ip}/rpc/Switch.Set",
        json={"id": 0, "on": turn_on}, timeout=3
    )
    return r.status_code == 200


def set_relay(device, turn_on):
    # try gen1 first, gen2/3 rpc as fallback
    ip = device["ip"]
    success = False
    try:
        success = _set_relay_gen1(ip, turn_on)
    except Exception:
        pass

    if not success:
        try:
            success = _set_relay_gen2(ip, turn_on)
        except Exception:
            pass

    if success:
        device["relay_on"] = turn_on
    return success
