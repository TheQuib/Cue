---
title: Director
weight: 6
---

Director is the desktop companion to Cue. It is an Electron app that runs on any machine on your local network and gives you a clean interface for sending commands to one display or all of them at once.

## Installation

Download the latest release for your platform from the [Director releases page](https://github.com/TheQuib/director/releases):

- **macOS** — `.dmg`
- **Windows** — `.exe`
- **Linux** — `.AppImage`

On macOS, if you see an "unidentified developer" warning, right-click the app and select **Open** to bypass it on first launch.

## Configuration

Director reads from a `config.yml` file. On first launch, it uses the default config shipped with the app. Any changes made through the settings UI are saved to a user config file that persists across updates:

- **macOS** — `~/Library/Application Support/director/config.yml`
- **Windows** — `%APPDATA%\director\config.yml`
- **Linux** — `~/.config/director/config.yml`

### Example config

```yaml
location: "Building A - Board Room"
api_key: "your-api-key"

displays:
  - id: your-pi-1
    name: "Left"
    host: 192.168.1.101
    port: 5000
    inputs: [1, 2]

  - id: your-pi-2
    name: "Center"
    host: 192.168.1.102
    port: 5000
    inputs: [1, 2]

  - id: your-pi-3
    name: "Right"
    host: 192.168.1.103
    port: 5000
    inputs: [1, 2]
```

### Config reference

| Field | Description |
|-------|-------------|
| `location` | Friendly name shown in the app header |
| `api_key` | Must match the `api_key` set on each Cue Pi |
| `displays[].id` | Unique identifier, used internally |
| `displays[].name` | Friendly name shown on the display card |
| `displays[].host` | IP address of the Pi |
| `displays[].port` | Port the Cue API is listening on (default: `5000`) |
| `displays[].inputs` | List of HDMI input numbers to show as buttons |

## Using Director

### Display cards

Each display gets a card showing its name, ID, host, and current status. On and Off buttons send the corresponding command to that display. HDMI input buttons appear for each input defined in the config.

### All displays

The **All On** and **All Off** buttons at the top send the command to every display simultaneously.

### Status dots

Each card has a status dot indicating the current state of that Pi:

| Color | Meaning |
|-------|---------|
| Green | Online and CEC bus ready |
| Amber | Online but CEC bus not ready |
| Red | Offline or unreachable |

Status is refreshed automatically every 15 seconds. Click the refresh button to check immediately.

### Settings

Click the gear icon in the top right to open the settings panel. From there you can update the location name, API key, and display list without editing the config file directly. Changes are saved immediately on clicking **Save**.

The settings panel also has buttons to open the config file in your system text editor or open the folder containing it, if you prefer to edit it manually.

## Multiple locations

To use Director in a different location, install it on a machine at that location and configure it with the appropriate Pis. Each instance only knows about the displays in its own config — there is no central server.
