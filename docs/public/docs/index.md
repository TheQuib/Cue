# Intro

Welcome to the Cue and Director documentation!

## What is Cue?

**Cue** is a lightweight display control service that sends CEC commands to HDMI-connected TVs from a Raspberry Pi. It can be deployed at scale across multiple devices using Ansible and Docker.

## The core idea

A Raspberry Pi sits connected to a display over HDMI, maintains a persistent CEC connection, and waits for a command. When one arrives via the REST API, Cue handles the full sequence — power on, input switching, standby — in the right order, with the right timing. The entire flow runs inside a Docker container on the Pi, deployed and managed by an Ansible playbook.

For managing deployments across many devices, Cue integrates with Ansible Semaphore, giving you a UI to handle inventory, variables, and job runs without touching a terminal.

## What is Director?

**Director** is the desktop companion to Cue. It's a lightweight Electron app that runs on any machine on your local network and gives you a simple interface for sending commands to one display or all of them at once. Configure it with a YAML file, point it at your Pis, and you have a control surface that works on Windows, macOS, and Linux.

## How it works

When a command is received at the `/command` endpoint, Cue's Python application reads your `config.yml` and executes the appropriate CEC sequence against the connected display.

Director talks to those endpoints directly over the local network, fanning commands out to all configured displays in parallel when needed.

## What you'll need

- A Raspberry Pi (any model with an HDMI port)
- A display with HDMI-CEC support (look for Anynet+, BRAVIA Sync, SimpLink, or EasyLink in your display settings)
- An Ansible control node or Semaphore instance
- A machine to run Director on (Windows, macOS, or Linux)

## Where to go next

If you're setting up for the first time, head to [Getting Started](./getting-started) to walk through Pi setup and deployment.

If you're already up and running and want to tune timing or configure inputs, jump to [Configuration](./configuration).

If you're managing multiple Pis through Semaphore, the [Semaphore](./semaphore) section covers inventory and variable setup.

If you're looking for the Director desktop app, head to [Director](./director).
