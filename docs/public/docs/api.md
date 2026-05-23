# API

Cue exposes a small REST API on each Pi. All requests require the `X-API-Key` header.

## Authentication

Every request must include the API key set in `config.yml`:

```
X-API-Key: your-api-key
```

Requests with a missing or incorrect key return `401 Unauthorized`.

## Endpoints

### `GET /health`

Returns the current status of the Cue service and CEC bus.

**Request**

```bash
curl -H "X-API-Key: yourkey" http://<pi-ip>:5000/health
```

**Response**

```json
{
  "status": "ok",
  "tv_id": "your-tv-id",
  "cec_client": "running",
  "bus_ready": true,
  "phys_addr": "2000"
}
```

| Field | Description |
|-------|-------------|
| `status` | Always `ok` if the API is reachable |
| `tv_id` | The friendly label set in `config.yml` |
| `cec_client` | `running` or `stopped` |
| `bus_ready` | `true` if the display is on the CEC bus, `false` if in deep sleep |
| `phys_addr` | The Pi's physical CEC address. `ffff` indicates the display has dropped off the bus |

---

### `POST /command`

Send a command to the display.

**Request**

```bash
curl -X POST http://<pi-ip>:5000/command \
  -H "Content-Type: application/json" \
  -H "X-API-Key: yourkey" \
  -d '{"command": "on"}'
```

**Body**

```json
{
  "command": "on"
}
```

**Commands**

| Command | Description |
|---------|-------------|
| `on` | Power on the display, assert Pi as active source, switch to content input |
| `off` | Assert Pi as active source, wait, then send standby |
| `input_hdmi1` | Switch to HDMI 1 |
| `input_hdmi2` | Switch to HDMI 2 |
| `input_hdmi3` | Switch to HDMI 3 |
| `input_hdmi4` | Switch to HDMI 4 |

**Response**

```json
{
  "status": "ok",
  "command": "on"
}
```

The API returns immediately — commands execute asynchronously in the background. Use `/health` to check the resulting bus state.

## Status codes

| Code | Meaning |
|------|---------|
| `200` | Command accepted |
| `400` | Missing or unknown command |
| `401` | Invalid or missing API key |
| `415` | Missing `Content-Type: application/json` header |
| `503` | CEC bus not ready (display in deep sleep). Note: the `on` command bypasses this check |

## Notes

- The `on` command bypasses the `bus_ready` check intentionally. The display must be woken even when it has dropped off the CEC bus entirely.
- Input switch commands (`input_hdmi*`) will fail with `503` if the display is in deep sleep, since switching inputs requires the display to already be on.
- Commands run in background threads. Sending multiple commands in quick succession may produce unexpected results — wait for one sequence to complete before sending the next.

