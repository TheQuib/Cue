---
title: Splash
weight: 5
---

Cue shows a splash image so an ugly command line or Raspberry Pi OS desktop doesn't show up when showing the Raspberry Pi TV input.

## Default

Cue ships with a default splash image with its name and description, which you can change and will be updated on the next Ansible push.

## Image requirements

Cue requires the image be:
 - 1920x1080 (16:9)
 - A `PNG` file named `splash.png`

## Updating the image

Just drop your custom `splash.png` file into the `/splash` directory.