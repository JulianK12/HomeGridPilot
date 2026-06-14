# HomeGridPilot

A small Flask web app for monitoring and controlling smart plugs/relays,
with optional automation based on dynamic electricity prices (aWattar Germany)
and PV (solar) surplus.

## Features

- Live overview of all configured devices (power, voltage, current, energy)
- Works with Shelly Gen1 (`/status`, `/relay/0?turn=`), Gen2/Gen3 (`/rpc/Switch.*`),
  Tasmota (`/cm?cmnd=...`) and TP-Link Kasa/Tapo (local port 9999) devices
- Per-device power history with sparkline and detail charts
- Special "PV" device type for monitoring solar production
- Current and today's electricity price from the aWattar Day-Ahead API (DE)
- Automation rules per device: turn on/off based on price (≤ X ct/kWh) and/or
  PV surplus (≥ Y W), combined with AND/OR logic and a priority for PV allocation
- Automation log showing what was switched and why
- Simple login (single user, in-memory)

## Requirements

- Python 3.10+
- See `requirements.txt`

```bash
pip install -r requirements.txt
```

## Project layout

```
app.py              Flask app: routes, sessions, login, automation loop
devices.py          Dispatches status/relay calls to the right protocol module
shelly.py           Shelly Gen1/Gen2/Gen3 interface
tasmota.py          Tasmota interface
tplink.py           TP-Link Kasa/Tapo interface
templates/
  dashboard.html    Main dashboard UI
  login.html        Login page
```

Each protocol module exposes the same two functions, `fetch_status(device)`
and `set_relay(device, turn_on)`. To support another interface, add a new
module with these two functions and register it in `devices.py`.

## Setup

Copy `.env.example` to `.env` and fill in real values:

```bash
cp .env.example .env
```

- `SECRET_KEY` – random key used to sign session cookies. Generate one with:
  ```bash
  python3 -c "import secrets; print(secrets.token_hex(32))"
  ```
- `ADMIN_USERNAME` / `ADMIN_PASSWORD` – login credentials for the dashboard.
  Pick your own password; it's hashed in memory on startup and never stored
  in plain text.
- `SESSION_COOKIE_SECURE` – set to `true` once the app is served over HTTPS.

If `SECRET_KEY` or `ADMIN_PASSWORD` are missing, the app falls back to an
insecure default and prints a warning on startup – fine for a quick local
test, not for anything reachable from outside your machine.

## Running

```bash
python3 app.py
```

The app starts on port 5000. Open it at:

```
http://127.0.0.1:5000
```

> On macOS, `localhost:5000` may not work because the AirPlay Receiver also
> listens on port 5000. Use `127.0.0.1:5000` instead, or disable AirPlay
> Receiver in System Settings.

## Login

Single user, configured via `ADMIN_USERNAME` / `ADMIN_PASSWORD` in `.env`
(defaults to `admin` / `admin123` if not set). The password is stored as a
salted hash in memory, sessions are signed, HTTP-only cookies with an 8 hour
lifetime, and repeated failed logins from the same IP are temporarily locked
out.

## Adding devices

Add a device via the UI with its IP address, interface and a type:

- **Interfaces**: Shelly (Gen1 / Gen2 / Gen3), Tasmota, TP-Link Kasa/Tapo
- `plug` – a regular relay/plug
- `pv` – a device measuring your PV inverter's output

PV devices are excluded from automation as switchable consumers and instead
contribute to the available PV surplus.

No real hardware on hand? Use the "Demo-Daten laden" button to populate the
dashboard with a few fake devices.

## Automation

Automation can be configured per device under its settings:

- **Price rule**: turn the device on when the current electricity price
  (plus an optional markup) is at or below a threshold
- **PV rule**: turn the device on once enough PV surplus is available
- **Logic**: combine both rules with AND or OR
- **Priority**: when PV surplus is limited, lower-priority numbers get
  served first

The global automation switch and interval are configured in Settings. When
enabled, a background thread periodically fetches the current price and PV
production, evaluates each device's rules, and switches relays accordingly.

## Notes

- Devices, their automation rules, power history, global automation settings
  and the automation log are persisted in a local SQLite database
  (`data.db`, created automatically on first run, git-ignored). The
  electricity price cache and login-lockout state remain in memory only and
  are rebuilt after a restart.
- Electricity prices come from the [aWattar API] (free for aWattar-Clients) (https://www.awattar.de/) –
  no API key required, but subject to their fair-use limits.
- This project is not affiliated with Shelly/Allterco Robotics, Tasmota,
  TP-Link Technologies (Kasa/Tapo) or aWattar.
- The Inter font (`static/fonts/`) is self-hosted under the
  [SIL Open Font License 1.1](https://openfontlicense.org/) so no requests
  go to Google Fonts.

## License

MIT – see [LICENSE](LICENSE).
