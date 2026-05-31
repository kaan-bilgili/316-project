"""Build a Windows release folder with PyInstaller (includes manual.txt).

Usage:
    pip install pyinstaller
    python build_release.py

The installer must ship the entire ``dist/IAE/`` folder (exe + _internal),
not only the .exe file. Bundled read-only assets: manual.txt, default configurations.
"""
from __future__ import annotations

import os
import subprocess
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
MANUAL = os.path.join(ROOT, "manual.txt")
CONFIGS = os.path.join(ROOT, "configurations")
SEP = ";" if sys.platform.startswith("win") else ":"


def main() -> int:
    if not os.path.isfile(MANUAL):
        print(f"ERROR: missing {MANUAL}", file=sys.stderr)
        return 1
    if not os.path.isdir(CONFIGS):
        print(f"ERROR: missing {CONFIGS}", file=sys.stderr)
        return 1

    add_data = [
        f"{MANUAL}{SEP}.",
        f"{CONFIGS}{SEP}configurations",
    ]
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        "IAE",
        *[f"--add-data={item}" for item in add_data],
        os.path.join(ROOT, "main.py"),
    ]
    print("Running:", " ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
