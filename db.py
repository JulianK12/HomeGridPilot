"""SQLite persistence for devices, power history, automation settings and log."""

import json
import os
import sqlite3
import threading

DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "data.db"))

_lock = threading.Lock()
_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
_conn.execute("PRAGMA journal_mode=WAL")

POWER_HISTORY_LIMIT = 60
AUTOMATION_LOG_LIMIT = 50

DEFAULT_AUTOMATION_SETTINGS = {
    "enabled": False,
    "interval_sec": 300,
    "price_markup_ct": 0.0,
}


def init_db():
    with _lock:
        _conn.executescript("""
            CREATE TABLE IF NOT EXISTS devices (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                ip TEXT NOT NULL,
                type TEXT NOT NULL,
                protocol TEXT NOT NULL,
                online INTEGER NOT NULL DEFAULT 0,
                relay_on INTEGER NOT NULL DEFAULT 0,
                power_w REAL NOT NULL DEFAULT 0,
                voltage_v REAL NOT NULL DEFAULT 0,
                current_a REAL NOT NULL DEFAULT 0,
                energy_kwh REAL NOT NULL DEFAULT 0,
                added TEXT NOT NULL,
                is_demo INTEGER NOT NULL DEFAULT 0,
                automation TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS power_history (
                device_id TEXT NOT NULL,
                ts TEXT NOT NULL,
                watt REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_power_history_device ON power_history(device_id);

            CREATE TABLE IF NOT EXISTS automation_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                enabled INTEGER NOT NULL,
                interval_sec INTEGER NOT NULL,
                price_markup_ct REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS automation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                device TEXT NOT NULL,
                action TEXT NOT NULL,
                reason_parts TEXT NOT NULL,
                logic TEXT NOT NULL
            );
        """)
        _conn.commit()


def _device_to_row(device):
    auto = device.get("automation", {})
    return (
        device["id"],
        device["name"],
        device["ip"],
        device["type"],
        device["protocol"],
        int(bool(device.get("online", False))),
        int(bool(device.get("relay_on", False))),
        float(device.get("power_w", 0.0)),
        float(device.get("voltage_v", 0.0)),
        float(device.get("current_a", 0.0)),
        float(device.get("energy_kwh", 0.0)),
        device["added"],
        int(bool(device.get("_demo", False))),
        json.dumps(auto),
    )


def _row_to_device(row):
    return {
        "id": row[0],
        "name": row[1],
        "ip": row[2],
        "type": row[3],
        "protocol": row[4],
        "online": bool(row[5]),
        "relay_on": bool(row[6]),
        "power_w": row[7],
        "voltage_v": row[8],
        "current_a": row[9],
        "energy_kwh": row[10],
        "added": row[11],
        **({"_demo": True} if row[12] else {}),
        "automation": json.loads(row[13]),
    }


def load_devices():
    with _lock:
        rows = _conn.execute("""
            SELECT id, name, ip, type, protocol, online, relay_on, power_w,
                   voltage_v, current_a, energy_kwh, added, is_demo, automation
            FROM devices
        """).fetchall()
    return {row[0]: _row_to_device(row) for row in rows}


def save_device(device):
    with _lock:
        _conn.execute("""
            INSERT INTO devices (id, name, ip, type, protocol, online, relay_on,
                                  power_w, voltage_v, current_a, energy_kwh, added,
                                  is_demo, automation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name, ip=excluded.ip, type=excluded.type,
                protocol=excluded.protocol, online=excluded.online,
                relay_on=excluded.relay_on, power_w=excluded.power_w,
                voltage_v=excluded.voltage_v, current_a=excluded.current_a,
                energy_kwh=excluded.energy_kwh, added=excluded.added,
                is_demo=excluded.is_demo, automation=excluded.automation
        """, _device_to_row(device))
        _conn.commit()


def delete_device(device_id):
    with _lock:
        _conn.execute("DELETE FROM devices WHERE id = ?", (device_id,))
        _conn.execute("DELETE FROM power_history WHERE device_id = ?", (device_id,))
        _conn.commit()


def load_power_history():
    with _lock:
        rows = _conn.execute("""
            SELECT device_id, ts, watt FROM power_history ORDER BY device_id, rowid ASC
        """).fetchall()
    history = {}
    for device_id, ts, watt in rows:
        history.setdefault(device_id, []).append({"ts": ts, "watt": watt})
    return history


def add_power_history_entry(device_id, ts, watt):
    with _lock:
        _conn.execute(
            "INSERT INTO power_history (device_id, ts, watt) VALUES (?, ?, ?)",
            (device_id, ts, watt),
        )
        _conn.execute("""
            DELETE FROM power_history
            WHERE device_id = ? AND rowid NOT IN (
                SELECT rowid FROM power_history WHERE device_id = ?
                ORDER BY rowid DESC LIMIT ?
            )
        """, (device_id, device_id, POWER_HISTORY_LIMIT))
        _conn.commit()


def replace_power_history(device_id, entries):
    with _lock:
        _conn.execute("DELETE FROM power_history WHERE device_id = ?", (device_id,))
        _conn.executemany(
            "INSERT INTO power_history (device_id, ts, watt) VALUES (?, ?, ?)",
            [(device_id, e["ts"], e["watt"]) for e in entries[-POWER_HISTORY_LIMIT:]],
        )
        _conn.commit()


def load_automation_settings():
    with _lock:
        row = _conn.execute(
            "SELECT enabled, interval_sec, price_markup_ct FROM automation_settings WHERE id = 1"
        ).fetchone()
        if row is None:
            settings = dict(DEFAULT_AUTOMATION_SETTINGS)
            _conn.execute(
                "INSERT INTO automation_settings (id, enabled, interval_sec, price_markup_ct) "
                "VALUES (1, ?, ?, ?)",
                (int(settings["enabled"]), settings["interval_sec"], settings["price_markup_ct"]),
            )
            _conn.commit()
            return settings
    return {
        "enabled": bool(row[0]),
        "interval_sec": row[1],
        "price_markup_ct": row[2],
    }


def save_automation_settings(settings):
    with _lock:
        _conn.execute("""
            INSERT INTO automation_settings (id, enabled, interval_sec, price_markup_ct)
            VALUES (1, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                enabled=excluded.enabled, interval_sec=excluded.interval_sec,
                price_markup_ct=excluded.price_markup_ct
        """, (int(settings["enabled"]), settings["interval_sec"], settings["price_markup_ct"]))
        _conn.commit()


def load_automation_log():
    with _lock:
        rows = _conn.execute("""
            SELECT ts, device, action, reason_parts, logic
            FROM automation_log ORDER BY id DESC LIMIT ?
        """, (AUTOMATION_LOG_LIMIT,)).fetchall()
    return [
        {
            "ts": ts,
            "device": device,
            "action": action,
            "reason_parts": json.loads(reason_parts),
            "logic": logic,
        }
        for ts, device, action, reason_parts, logic in rows
    ]


def insert_automation_log(entry):
    with _lock:
        _conn.execute("""
            INSERT INTO automation_log (ts, device, action, reason_parts, logic)
            VALUES (?, ?, ?, ?, ?)
        """, (entry["ts"], entry["device"], entry["action"],
              json.dumps(entry.get("reason_parts", [])), entry.get("logic", "OR")))
        _conn.execute("""
            DELETE FROM automation_log
            WHERE id NOT IN (SELECT id FROM automation_log ORDER BY id DESC LIMIT ?)
        """, (AUTOMATION_LOG_LIMIT,))
        _conn.commit()
