# About

Some problems are too small to buy a solution for and too annoying to leave alone.

Cue came out of one of those. A handful of displays, a remote that worked until it didn't, and the kind of stubborn curiosity that turns a Saturday afternoon fix into a weeks-long detour through HDMI-CEC specs, Raspberry Pi internals, and the surprisingly opinionated world of commercial display firmware. Along the way there were dead ends, a few Samsung displays that really did not want to be told what to do, and enough `errno=64` errors to last a lifetime.

## Cue

Cue runs on a Raspberry Pi and sends CEC commands to a display. It exposes a REST API for power on, standby, and input switching. Ansible and Semaphore handle deployment, so rolling it out to one display or twenty is the same amount of work.

## Director

Director is the desktop companion to Cue. It's an Electron app that runs on any machine on the local network and gives you a clean interface for sending commands to one display or all of them at once. Configure it with a simple YAML file, point it at your Pis, and you've got a control surface that works on any OS without installing anything else.

For anyone who has ever handed an IR remote to someone and watched them aim it at the wrong thing, Director is the alternative.

## Built with

- [Raspberry Pi](https://www.raspberrypi.com/)
- [libCEC](https://github.com/Pulse-Eight/libcec)
- [Flask](https://flask.palletsprojects.com/)
- [Docker](https://www.docker.com/)
- [Ansible](https://www.ansible.com/)
- [Ansible Semaphore](https://www.semaphoreui.com/)
- [Electron](https://www.electronjs.org/)
