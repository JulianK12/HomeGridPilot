"""Dispatches device status/relay calls to the right protocol module."""

import shelly
import tasmota
import tplink

PROTOCOL_MODULES = {
    "shelly": shelly,
    "tasmota": tasmota,
    "tplink": tplink,
}

PROTOCOLS = tuple(PROTOCOL_MODULES.keys())


def _module_for(device):
    return PROTOCOL_MODULES.get(device.get("protocol", "shelly"), shelly)


def fetch_status(device):
    return _module_for(device).fetch_status(device)


def set_relay(device, turn_on):
    return _module_for(device).set_relay(device, turn_on)
