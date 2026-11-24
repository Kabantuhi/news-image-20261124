#!/usr/bin/env python3
"""Validate entry.png and copy it to the output directory (stdlib only).

Usage:
    python3 main.py            # copies entry.png to /output/entry.png
    python3 main.py <outdir>   # copies entry.png to <outdir>/entry.png
"""
import struct
import sys
from pathlib import Path


def main():
    here = Path(__file__).resolve().parent
    src = here / "entry.png"
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    data = src.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("entry.png is not a PNG")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (1024, 1024):
        raise SystemExit(f"entry.png is {width}x{height}, expected 1024x1024")
    if len(data) > 1024 * 1024:
        raise SystemExit(f"entry.png is {len(data)} bytes, over the 1 MiB limit")
    dest = out_dir / "entry.png"
    dest.write_bytes(data)
    print(f"wrote {dest} ({len(data)} bytes, 1024x1024)")


if __name__ == "__main__":
    main()
