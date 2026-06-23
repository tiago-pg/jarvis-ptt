#!/usr/bin/env python3
"""Gera o ícone Jarvis.icns para o app."""
import struct
import subprocess
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).parent


def _create_png(width: int, height: int) -> bytes:
    pixels = bytearray()
    cx, cy = width // 2, height // 2
    radius = width // 2 - 2
    radius2 = radius * radius

    for y in range(height):
        row = bytearray()
        for x in range(width):
            dx, dy = x - cx, y - cy
            dist2 = dx * dx + dy * dy
            if dist2 <= radius2:
                frac = dist2 / radius2
                r = int(30 + (1 - frac) * 40)
                g = int(80 + (1 - frac) * 60)
                b = int(180 + (1 - frac) * 50)
                row.extend([r, g, b, 255])
            else:
                row.extend([0, 0, 0, 0])
        pixels.append(0)
        pixels.extend(row)

    def chunk(chunk_type: bytes, data: bytes) -> bytes:
        c = chunk_type + data
        crc = struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack(">I", len(data)) + c + crc

    sig = b"\x89PNG\r\n\x1a\n"
    # color type 6 = RGBA
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    raw = zlib.compress(bytes(pixels))
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", raw) + chunk(b"IEND", b"")


def main():
    sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]

    iconset = HERE / "Jarvis.iconset"
    iconset.mkdir(exist_ok=True)

    for size, name in sizes:
        png_data = _create_png(size, size)
        (iconset / name).write_bytes(png_data)
        print(f"  Criado {name} ({size}x{size})")

    menu_icon = _create_png(32, 32)
    (HERE / "jarvis_icon.png").write_bytes(menu_icon)
    print("  Criado jarvis_icon.png (32x32)")

    if sys.platform == "darwin":
        print("\nConvertendo para .icns com iconutil...")
        result = subprocess.run(
            ["iconutil", "-c", "icns", str(iconset), "-o", str(HERE / "Jarvis.icns")],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            print("  Jarvis.icns criado!")
        else:
            print(f"  iconutil falhou: {result.stderr}")
    else:
        print("\n(iconutil só roda no macOS - pulei criacao do .icns)")
        print("  No Mac, rode: iconutil -c icns Jarvis.iconset -o Jarvis.icns")

    print("Icones gerados!")


if __name__ == "__main__":
    main()
