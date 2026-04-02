# camera-edge-agent

IoT edge agent that runs on the machine co-located with camera hardware. Maintains a persistent WebSocket connection to the [camera-control-panel](https://github.com/rashidiy/camera-control-panel) backend, auto-provisions per-device systemd services, and relays HTTP requests to local camera devices — including Digest auth and base64-encoded image responses.

---

## Where it fits

```
camera-control-panel (remote server)
          │
          │  WebSocket (wss://)
          ▼
  CompanyConsumer (main.py)
   ├── event: company.new_device
   │       └── create_service_file() → write .service → systemctl enable + start
   ├── event: company.delete_device
   │       └── delete_service() → rm .service → systemctl daemon-reload
   └── event: send_request
           └── HTTP relay to local camera → return response

          │  (one systemd process per device)
          ▼
  DeviceClient (device_client.py)  ←→  Camera hardware (local network)
          │
          │  WebSocket (wss://)  →  /device/{device_id}/?security_key=...
          └── event: send_request → forward HTTP → return status + body + base64 content
```

Two WebSocket connections are maintained:
- **Company-level** (`main.py`): receives company-wide events like new/deleted devices
- **Device-level** (`device_client.py`): one per physical device, handles per-device HTTP relay

---

## Auto-provisioning via systemd

When a new device is added in the control panel, the panel sends a `company.new_device` WebSocket event. The agent:

1. Reads `template.txt` (systemd unit template)
2. Fills in `description`, `ExecStart`, `Environment`
3. Writes `/etc/systemd/system/dev_{device_id}.service`
4. Runs `systemctl enable dev_{device_id}` and `systemctl start dev_{device_id}`

The generated unit has `Restart=always` and `RestartSec=6` — the device client survives crashes and reboots without manual intervention.

When a device is deleted from the panel, a `company.delete_device` event triggers service file removal and `systemctl daemon-reload`.

**Zero manual provisioning**: adding a camera in the web UI is all that's needed.

---

## HTTP relay with Digest auth

When the control panel needs to send a command to a specific camera (e.g., get a snapshot, push a permission), it sends a `send_request` WebSocket message to the device agent. The agent:

1. Parses the request (method, URL, headers, body)
2. Sends it to the local camera using `requests` with HTTPDigestAuth
3. For CGI/picture endpoints: encodes the response body as base64
4. Returns `{status_code, text, content_base64}` back over WebSocket

The control panel never talks to the camera directly — it goes through this relay. This avoids firewall issues (cameras are on local networks) and centralizes auth credential management.

---

## Environment variables

| Variable | Description |
|---|---|
| `COMPANY_ID` | Company UUID from the control panel |
| `SECURITY_KEY` | Auth key for WebSocket handshake |
| `HOST` | Control panel hostname |
| `PORT` | WebSocket port (typically 443) |
| `PY_PATH` | Python interpreter path used in generated systemd unit files |

---

## Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| WebSocket | websockets 12 |
| HTTP client | requests (HTTPDigestAuth) |
| Service management | subprocess + systemctl |
| Config | python-dotenv |

---

## Getting started

```bash
pip install -r requirements.txt

cp .env.example .env
# set COMPANY_ID, SECURITY_KEY, HOST, PORT, PY_PATH

python main.py
```

Run as a systemd service for production:
```ini
[Service]
ExecStart=/path/to/venv/bin/python /path/to/main.py
Restart=always
RestartSec=6
```

The device client services are created automatically when cameras are added through the control panel.
