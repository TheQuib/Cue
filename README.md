# Cue

Send CEC commands to TVs at scale with just a Raspberry Pi and Ansible.

Cue runs a persistent `cec-client` connection on each Pi, exposed via a small REST API. This keeps the Pi on the CEC bus at all times — allowing reliable wake from deep sleep states that one-shot CEC commands can't reach.

---

## tl;dr

- Each Pi runs a Docker container with a persistent `cec-client` process and a Flask REST API
- Commands are sent via HTTP POST to the Pi's local API
- Ansible Semaphore deploys and manages all Pis
- Stream Deck buttons trigger Semaphore job templates via webhook

---

## API

### `GET /health`
Returns the status of the container and cec-client process.

```json
{
  "status": "ok",
  "cec_client": "running",
  "tv_id": "ad-br-tv-l"
}
```

### `POST /command`
Send a command to the TV.

```json
{ "command": "on" }
```

| Command       | Action                                          |
|---------------|-------------------------------------------------|
| `on`          | Power on, assert Pi as active source, switch to content input |
| `off`         | Assert Pi as active source, standby             |
| `input_hdmi1` | Switch to HDMI 1                                |
| `input_hdmi2` | Switch to HDMI 2                                |
| `input_hdmi3` | Switch to HDMI 3                                |
| `input_hdmi4` | Switch to HDMI 4                                |

---

## Configuration (`config.yml`)

| Variable            | Default       | Description                                      |
|---------------------|---------------|--------------------------------------------------|
| `tv_id`             | `tv-unknown`  | Friendly name, used in logs and health endpoint  |
| `cec_device`        | `/dev/cec0`   | CEC adapter device path                          |
| `pi_hdmi_port`      | `2`           | HDMI port the Pi is connected to                 |
| `content_hdmi_port` | `1`           | HDMI port the content source is on               |
| `api_port`          | `5000`        | Port the REST API listens on                     |
| `on_delay`          | `1`           | Seconds between `on 0` and `as`                  |
| `input_delay`       | `3`           | Seconds between `as` and switching content input |
| `off_delay`         | `2`           | Seconds between `as` and `standby 0`             |

---

## Setup

### Semaphore Inventory

```yaml
all:
  hosts:
    ad-br-tv-l:
      ansible_host: 192.168.1.101
      ansible_user: pi
      tv_id: ad-br-tv-l
      pi_hdmi_port: 2
      content_hdmi_port: 1
      on_delay: 1
      input_delay: 3
      off_delay: 2
    ad-br-tv-c:
      ansible_host: 192.168.1.102
      ansible_user: pi
      tv_id: ad-br-tv-c
      pi_hdmi_port: 2
      content_hdmi_port: 1
    ad-br-tv-r:
      ansible_host: 192.168.1.103
      ansible_user: pi
      tv_id: ad-br-tv-r
      pi_hdmi_port: 2
      content_hdmi_port: 1
```

### Semaphore Job Templates

| Template Name       | Target host   |
|---------------------|---------------|
| Deploy - All TVs    | all hosts     |
| Deploy - TV Left    | `ad-br-tv-l`  |
| Deploy - TV Center  | `ad-br-tv-c`  |
| Deploy - TV Right   | `ad-br-tv-r`  |

### Stream Deck Integration

Each Stream Deck button POSTs to the Pi's API directly or via a Semaphore webhook:

```
POST http://<pi-ip>:5000/command
Content-Type: application/json

{ "command": "on" }
```

---

## Pi Naming Convention

| Hostname      | Location        |
|---------------|-----------------|
| `ad-br-tv-l`  | AD / BR / Left  |
| `ad-br-tv-c`  | AD / BR / Center|
| `ad-br-tv-r`  | AD / BR / Right |

---

## About

Inspired by [Rondo](https://github.com/TheQuib/Rondo) — same Pi + Ansible + Semaphore pattern, opposite direction.
