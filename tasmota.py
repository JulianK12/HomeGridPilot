"""Interface for Tasmota devices (plain HTTP API on port 80)."""

import requests

OFFLINE_STATUS = {
    "online": False, "relay_on": False,
    "power_w": 0, "voltage_v": 0, "current_a": 0, "energy_kwh": 0,
}


def fetch_status(device):
    ip = device["ip"]
    try:
        r = requests.get(f"http://{ip}/cm", params={"cmnd": "Status 0"}, timeout=3)
        if r.status_code == 200:
            s = r.json()
            sts = s.get("StatusSTS", {})
            energy = sts.get("ENERGY", s.get("StatusSNS", {}).get("ENERGY", {}))
            return {
                "online": True,
                "relay_on": sts.get("POWER", "OFF") == "ON",
                "power_w": round(energy.get("Power", 0.0), 2),
                "voltage_v": round(energy.get("Voltage", 0.0), 1),
                "current_a": round(energy.get("Current", 0.0), 3),
                "energy_kwh": round(energy.get("Total", 0.0), 4),
            }
    except Exception:
        pass
    return dict(OFFLINE_STATUS)


def set_relay(device, turn_on):
    ip = device["ip"]
    try:
        cmnd = "Power On" if turn_on else "Power Off"
        r = requests.get(f"http://{ip}/cm", params={"cmnd": cmnd}, timeout=3)
        if r.status_code == 200:
            device["relay_on"] = turn_on
            return True
    except Exception:
        pass
    return False
