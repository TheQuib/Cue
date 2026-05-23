# Cue

Send CEC commands to TVs at scale with just a Raspberry Pi and Ansible.

Cue runs a persistent `cec-client` connection on each Pi, exposed via a small REST API. This keeps the Pi on the CEC bus at all times, allowing reliable wake from deep sleep states that one-shot CEC commands cannot reach.

---

## tl;dr

- Each Pi runs a Docker container with a persistent `cec-client` process and a Flask REST API
- Commands are sent via HTTP POST to the Pi's local API
- Ansible Semaphore deploys and manages all Pis
- Stream Deck buttons (or any HTTP client) hit the Pi APIs directly at runtime
- Semaphore is a deployment tool only, not a runtime dependency

---

## How it works

### Deployment workflow
Semaphore runs `deploy-cue.yml` against your inventory of Pis. It installs Docker, generates a config file from your Semaphore variables, and starts the container. Run this once on setup, and again any time you update the code or change config values.

### Runtime workflow
Each button press on the Stream Deck sends an HTTP POST directly to the target Pi's API on port 5000. No Semaphore involvement at runtime.

---

## API

All endpoints require the `X-API-Key` header.

### `GET /health`

Returns the current status of the container and CEC bus.

```json
{
  "status": "ok",
  "tv_id": "your-tv-id",
  "cec_client": "running",
  "bus_ready": true,
  "phys_addr": "2000"
}
```

### `POST /command`

Send a command to the TV.

```json
{ "command": "on" }
```

| Command       | Action                                                               |
|---------------|----------------------------------------------------------------------|
| `on`          | Power on, assert Pi as active source, switch to content HDMI port   |
| `off`         | Assert Pi as active source, wait, then standby                      |
| `input_hdmi1` | Switch to HDMI 1                                                     |
| `input_hdmi2` | Switch to HDMI 2                                                     |
| `input_hdmi3` | Switch to HDMI 3                                                     |
| `input_hdmi4` | Switch to HDMI 4                                                     |

Example:
```bash
curl -X POST http://<pi-ip>:5000/command \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"command": "on"}'
```

---

## Configuration

### `config.yml`

| Variable            | Default      | Description                                           |
|---------------------|--------------|-------------------------------------------------------|
| `tv_id`             | `tv-unknown` | Friendly label shown in the health endpoint           |
| `api_key`           | `changeme`   | Required on all requests via `X-API-Key` header. Generate with `openssl rand -hex 32` |
| `pi_hdmi_port`      | `2`          | HDMI port the Pi is connected to                      |
| `content_hdmi_port` | `1`          | HDMI port the content source is on                    |
| `api_port`          | `5000`       | Port the REST API listens on                          |
| `on_delay`          | `1`          | Seconds between `on 0` and `as`                       |
| `input_delay`       | `3`          | Seconds between `as` and switching to content input   |
| `off_delay`         | `2`          | Seconds between `as` and `standby 0`                  |

### Semaphore variables

Set these in Semaphore before running the deploy playbook.

| Variable        | Where to set       | Description                                      |
|-----------------|--------------------|--------------------------------------------------|
| `cue_api_key`   | Semaphore secret   | API key written to each Pi's config. Use the same value across all Pis |
| `semaphore_ip`  | Semaphore variable | IP of the Semaphore server, used to set firewall rules on each Pi |

### Semaphore inventory

```yaml
all:
  hosts:
    your-pi-1:
      ansible_host: 192.168.1.101
      ansible_user: pi
      tv_id: your-pi-1
      pi_hdmi_port: 2
      content_hdmi_port: 1
      on_delay: 1
      input_delay: 3
      off_delay: 2
    your-pi-2:
      ansible_host: 192.168.1.102
      ansible_user: pi
      tv_id: your-pi-2
      pi_hdmi_port: 2
      content_hdmi_port: 1
    your-pi-3:
      ansible_host: 192.168.1.103
      ansible_user: pi
      tv_id: your-pi-3
      pi_hdmi_port: 2
      content_hdmi_port: 1
```

---

## Security

Cue uses two layers of security:

**API key authentication**
Every request must include a matching `X-API-Key` header. Requests without a valid key return `401 Unauthorized`. The key is set via `cue_api_key` in Semaphore and written to each Pi's config at deploy time.

**Firewall**
The deploy playbook uses `iptables` to restrict port 5000 to the Semaphore server IP only, dropping all other inbound connections on that port. Rules are saved to `/etc/iptables/rules.v4` and persist across reboots.

---

## GitHub Actions

**`ci.yml`**
Runs on every push to `main` and every pull request. Lints Python with `flake8`, lints the Ansible playbook with `ansible-lint`, and does a test build of the Docker image for `arm64`.

**`publish.yml`**
Runs when a GitHub Release is created. Builds the Docker image for `arm64` and pushes it to GitHub Container Registry as `ghcr.io/<your-username>/cue:latest` and `ghcr.io/<your-username>/cue:<version>`.

After the first publish, set the package visibility to public in GitHub so the Pis can pull without authenticating:
1. Go to your GitHub profile, then Packages
2. Find the `cue` package
3. Package settings, then change visibility to Public

---

## Notes

- The `on` command bypasses the bus ready check intentionally. Some TVs drop off the CEC bus entirely in deep sleep, so the power on command must be sent regardless of bus state.
- The `off` and input commands require the bus to be ready since they only make sense when the TV is already on.
- `tv_id` is informational only. It appears in the `/health` response to identify which Pi you are talking to.
- Timing values (`on_delay`, `input_delay`, `off_delay`) may need tuning depending on your TV model and how quickly it responds to CEC commands.

---

## About

Inspired by [Rondo](https://github.com/TheQuib/Rondo), same Pi + Ansible + Semaphore pattern, opposite direction.
