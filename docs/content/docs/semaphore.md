---
title: Semaphore
weight: 4
---

Cue is designed to be deployed and managed through [Ansible Semaphore](https://www.semaphoreui.com/), which gives you a UI for handling inventory, secrets, and job runs across multiple Pis without touching a terminal.

## Setup overview

1. Add your repository to Semaphore
2. Create an inventory with your Pi host definitions
3. Create an environment with your secrets
4. Create a job template pointing at `deploy-cue.yml`
5. Run the job

## Inventory

Create a new inventory in Semaphore using the **Static YAML** type. Define one host per Pi:

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
      bus_wait_timeout: 15
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

Only `ansible_host`, `ansible_user`, and `tv_id` are required per host. All timing and port values fall back to defaults if not specified.

## Environment (secrets)

Create a new environment in Semaphore and add the following variables:

| Variable        | Type   | Description                                                  |
|-----------------|--------|--------------------------------------------------------------|
| `cue_api_key`   | Secret | API key written to each Pi's config. Use the same value across all Pis. Generate with `openssl rand -hex 32` |
| `semaphore_ip`  | Variable | IP address of the Semaphore server, used to set firewall rules on each Pi |

Mark `cue_api_key` as a **secret** so it is encrypted at rest and never shown in logs.

## Job template

Create a job template with the following settings:

| Field | Value |
|-------|-------|
| Name | `Deploy Cue` |
| Playbook | `deploy-cue.yml` |
| Inventory | your inventory |
| Environment | your environment |
| Repository | your Cue repository |

## Running a deployment

Click **Run** on the job template. Semaphore will SSH into each Pi in the inventory, install dependencies, generate the config file, and start or restart the Cue container.

Subsequent deployments are safe to run at any time. The container is recreated on each run with `--force-recreate`, so config changes take effect immediately.

## Per-host vs global variables

Variables defined in the inventory apply per host. Variables defined in the environment apply globally to all hosts in a run.

Use the inventory for things that differ between Pis — display IDs, HDMI port assignments, timing values. Use the environment for things shared across all Pis — the API key and Semaphore IP.
