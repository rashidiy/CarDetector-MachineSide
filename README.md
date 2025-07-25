# CarDetector-MachineSide

Machine-side client for the car detection system. Runs on the hardware host next to a car detector device — connects to the central server via WebSocket and manages per-device systemd services automatically.

## Stack

- Python 3.11+
- `asyncio`, `websockets`
- `requests` (with HTTPDigest auth for camera devices)
- `systemd` (via subprocess) for service lifecycle management
- `python-dotenv`

## How It Works

1. `main.py` connects to the server WebSocket as a company consumer
2. On `company.new_device` — creates a `.service` file from a template and registers/starts it via systemd
3. On `company.delete_device` — removes the service file and reloads systemd
4. On `send_request` — forwards HTTP requests (including Digest auth) to local camera hardware and returns the response (including base64-encoded images for snapshot endpoints)

Each device runs as its own independent systemd service, making the system resilient to restarts.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # set HOST, PORT, COMPANY_ID, SECURITY_KEY, PY_PATH
python main.py
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `HOST` | Server hostname |
| `PORT` | Server port (default: 443) |
| `COMPANY_ID` | Company UUID from the control panel |
| `SECURITY_KEY` | Auth key for WebSocket connection |
| `PY_PATH` | Python interpreter path for generated services |

## Service Registration

When a new device is added via the control panel, this client:
- Writes `/etc/systemd/system/dev_<device_id>.service`
- Runs `systemctl enable` and `systemctl start`

When a device is removed:
- Deletes the service file
- Reloads the systemd daemon
