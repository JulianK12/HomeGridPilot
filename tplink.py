"""Interface for TP-Link Kasa/Tapo devices (HS1xx/KP1xx).

Local TCP protocol on port 9999, JSON payloads wrapped in a simple
XOR "encryption" with a rotating key.
"""

import json
import socket
import struct

OFFLINE_STATUS = {
    "online": False, "relay_on": False,
    "power_w": 0, "voltage_v": 0, "current_a": 0, "energy_kwh": 0,
}


def _encrypt(payload):
    key = 171
    out = bytearray()
    for b in payload.encode():
        key ^= b
        out.append(key)
    return struct.pack(">I", len(out)) + bytes(out)


def _decrypt(data):
    key = 171
    out = bytearray()
    for b in data:
        out.append(b ^ key)
        key = b
    return out.decode()


def _request(ip, payload):
    with socket.create_connection((ip, 9999), timeout=3) as sock:
        sock.send(_encrypt(json.dumps(payload)))
        data = sock.recv(4096)
    return json.loads(_decrypt(data[4:]))


def fetch_status(device):
    ip = device["ip"]
    try:
        resp = _request(ip, {"system": {"get_sysinfo": {}}, "emeter": {"get_realtime": {}}})
        sysinfo = resp.get("system", {}).get("get_sysinfo", {})
        emeter = resp.get("emeter", {}).get("get_realtime", {})
        if "power_mw" in emeter:
            power = emeter["power_mw"] / 1000.0
            voltage = emeter.get("voltage_mv", 0) / 1000.0
            current = emeter.get("current_ma", 0) / 1000.0
            energy = emeter.get("total_wh", 0) / 1000.0
        else:
            power = emeter.get("power", 0.0)
            voltage = emeter.get("voltage", 0.0)
            current = emeter.get("current", 0.0)
            energy = emeter.get("total", 0.0)
        return {
            "online": True,
            "relay_on": bool(sysinfo.get("relay_state", 0)),
            "power_w": round(power, 2),
            "voltage_v": round(voltage, 1),
            "current_a": round(current, 3),
            "energy_kwh": round(energy, 4),
        }
    except Exception:
        pass
    return dict(OFFLINE_STATUS)


def set_relay(device, turn_on):
    ip = device["ip"]
    try:
        _request(ip, {"system": {"set_relay_state": {"state": 1 if turn_on else 0}}})
        device["relay_on"] = turn_on
        return True
    except Exception:
        return False
