import os
import sys


def get_resource_path(relative_path: str) -> str:
    """Return an absolute path to bundled resources (supports PyInstaller)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)


def normalize_to_absolute_path(path: str) -> str:
    """Normalize relative paths to absolute paths from current working dir."""
    if not path:
        return path
    if os.path.isabs(path):
        return os.path.normpath(path)
    return os.path.normpath(os.path.abspath(path))
