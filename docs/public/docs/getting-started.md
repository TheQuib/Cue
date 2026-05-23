# Getting Started

This page walks through setting up Cue on a Raspberry Pi for the first time.

## Prerequisites

Before you begin, make sure you have:

- A Raspberry Pi with a full HDMI port
- A display with HDMI-CEC enabled (look for Anynet+, BRAVIA Sync, SimpLink, or EasyLink in your display's settings — it is often off by default)
- An HDMI cable connecting the Pi to the display
- Raspberry Pi OS installed and SSH access configured
- Docker and Docker Compose installed on the Pi
- An Ansible control node or Semaphore instance

## Enable CEC on your display

Before anything else, make sure CEC is enabled on your display. The setting name varies by manufacturer but is usually found under:

- **Samsung** — `Menu → General → External Device Manager → Anynet+ (HDMI-CEC)`
- **LG** — `Settings → General → SIMPLINK (HDMI-CEC)`
- **Sony** — `Settings → External Inputs → Bravia Sync Settings`
- **Others** — check your display's manual for "HDMI-CEC" or one of the brand names above

## Verify CEC is working

SSH into your Pi and run a quick scan to confirm the display is visible on the CEC bus:

```bash
sudo apt update && sudo apt install -y cec-utils
echo "scan" | cec-client -s -d 1
```

You should see your display listed as a device with a physical address. If nothing shows up, double-check that CEC is enabled on the display and that your HDMI cable is fully seated.

## Deploy Cue

Cue is deployed using the included Ansible playbook. From your Ansible control node or Semaphore instance:

1. Clone the Cue repository
2. Set up your inventory with your Pi's IP address and variables (see [Configuration](./configuration) and [Semaphore](./semaphore))
3. Run the playbook:

```bash
ansible-playbook deploy-cue.yml -i your-inventory.yml
```

The playbook will install Docker, generate the config file, and start the Cue container on the Pi.

## Verify Cue is running

Once deployed, check that the container is up and the API is responding:

```bash
curl -H "X-API-Key: yourkey" http://<pi-ip>:5000/health
```

You should get back something like:

```json
{
  "status": "ok",
  "tv_id": "your-tv-id",
  "cec_client": "running",
  "bus_ready": true,
  "phys_addr": "2000"
}
```

If `bus_ready` is `false`, the display may be in standby or deep sleep. This is normal — the `on` command will still attempt to wake it.

## Next steps

- Head to [Configuration](./configuration) to understand all available config values
- Head to [Semaphore](./semaphore) to set up multi-Pi deployments
- Head to [API](./api) to start sending commands
- Head to [Director](./director) to install the desktop control app

