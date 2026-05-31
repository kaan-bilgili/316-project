"""Build a Windows release folder with PyInstaller (includes manual.txt).

Usage:
    pip install pyinstaller
    python build_release.py

The installer must ship the entire ``dist/IAE/`` folder (exe + _internal),
not only the .exe file. ``manual.txt`` is bundled into _internal via --add-data.
"""
from __future__ import annotations

import os
import subprocess
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
MANUAL = os.path.join(ROOT, "manual.txt")
SEP = ";" if sys.platform.startswith("win") else ":"


def main() -> int:
    if not os.path.isfile(MANUAL):
        print(f"ERROR: missing {MANUAL}", file=sys.stderr)
        return 1

    add_data = f"{MANUAL}{SEP}."
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        "IAE",
        f"--add-data={add_data}",
        os.path.join(ROOT, "main.py"),
    ]
    print("Running:", " ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
