"""Write a splash image directly to the Linux framebuffer (/dev/fb0).

No TTY or display server required. The image stays on screen until
something else writes to the framebuffer.
"""

import os
import struct
import sys

from PIL import Image

FB = "/dev/fb0"
TTY1 = "/dev/tty1"
VSIZE = "/sys/class/graphics/fb0/virtual_size"
BPP = "/sys/class/graphics/fb0/bits_per_pixel"
CURSOR_BLINK = "/sys/class/graphics/fbcon/cursor_blink"

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
    img = img.convert("RGBA")
    r, g, b, a = img.split()
    return Image.merge("RGBA", (b, g, r, a)).tobytes()


def suppress_console() -> None:
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


def display(image_path: str) -> None:
    """Write the splash image to the framebuffer. Raises on error."""
    w, h, bpp = fb_info()
    img = Image.open(image_path).resize((w, h), Image.LANCZOS)

    if bpp == 32:
        data = to_bgra32(img)
    elif bpp == 16:
        data = to_rgb565(img)
    else:
        raise ValueError(f"Unsupported framebuffer depth: {bpp} bpp")

    suppress_console()
    with open(FB, "wb") as fb:
        fb.write(data)
    suppress_console()


def main():
    image_path = sys.argv[1] if len(sys.argv) > 1 else "/home/pi/cue/splash.png"
    display(image_path)


if __name__ == "__main__":
    main()
