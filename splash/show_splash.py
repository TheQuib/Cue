#!/usr/bin/env python3
"""Write a splash image directly to the Linux framebuffer (/dev/fb0).

No TTY or display server required. Run as root (or a user with write
access to /dev/fb0).  The image stays on screen until something else
writes to the framebuffer.

Usage:
    python3 show_splash.py [image_path]

image_path defaults to /home/pi/cue/splash.png.
"""

import struct
import sys

from PIL import Image

FB = "/dev/fb0"
TTY1 = "/dev/tty1"
VSIZE = "/sys/class/graphics/fb0/virtual_size"
BPP = "/sys/class/graphics/fb0/bits_per_pixel"
CURSOR_BLINK = "/sys/class/graphics/fbcon/cursor_blink"

# ANSI: hide cursor + clear screen + move to top-left
_ANSI_SUPPRESS = b"\033[?25l\033[2J\033[H"


def fb_info():
    with open(VSIZE) as f:
        w, h = map(int, f.read().strip().split(","))
    with open(BPP) as f:
        bpp = int(f.read().strip())
    return w, h, bpp


def to_rgb565(img: Image.Image) -> bytes:
    img = img.convert("RGB")
    buf = bytearray(img.width * img.height * 2)
    idx = 0
    for r, g, b in img.getdata():
        pixel = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        struct.pack_into("<H", buf, idx, pixel)
        idx += 2
    return bytes(buf)


def to_bgra32(img: Image.Image) -> bytes:
    """Convert to 32-bit BGRA — the standard Pi framebuffer channel order."""
    img = img.convert("RGBA")
    r, g, b, a = img.split()
    return Image.merge("RGBA", (b, g, r, a)).tobytes()


def suppress_console() -> None:
    """Stop the framebuffer console from drawing over our image.

    1. Disable the blinking cursor via sysfs (if available).
    2. Send ANSI escape codes to tty1 to clear any on-screen text and
       hide the cursor — this must happen both before and after the
       framebuffer write so the console doesn't sneak text in between.
    """
    try:
        with open(CURSOR_BLINK, "w") as f:
            f.write("0")
    except OSError:
        pass

    try:
        with open(TTY1, "wb") as tty:
            tty.write(_ANSI_SUPPRESS)
    except OSError:
        pass


def main():
    image_path = sys.argv[1] if len(sys.argv) > 1 else "/home/pi/cue/splash.png"

    w, h, bpp = fb_info()
    img = Image.open(image_path).resize((w, h), Image.LANCZOS)

    if bpp == 32:
        data = to_bgra32(img)
    elif bpp == 16:
        data = to_rgb565(img)
    else:
        print(f"Unsupported framebuffer depth: {bpp} bpp", file=sys.stderr)
        sys.exit(1)

    # Clear the console before writing so its text doesn't show through.
    suppress_console()

    with open(FB, "wb") as fb:
        fb.write(data)

    # Clear again after writing — any console activity during the write
    # (late boot messages, cursor redraws) would otherwise leave artefacts.
    suppress_console()


if __name__ == "__main__":
    main()
