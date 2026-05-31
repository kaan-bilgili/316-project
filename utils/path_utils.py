import os
import sys


def get_resource_path(relative_path: str) -> str:
    """Return an absolute path to bundled resources (supports PyInstaller)."""
    # When bundled by PyInstaller `sys.frozen` is True.
    # - In onefile mode PyInstaller extracts to a temp folder and sets sys._MEIPASS.
    # - In onedir mode there's no _MEIPASS; resources are next to the executable.
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", None)
        if not base:
            # one-dir build: resources live alongside the executable
            base = os.path.dirname(sys.executable)
        return os.path.join(base, relative_path)

    # Normal (not frozen) execution: resolve relative to project root (cwd may vary).
    # Prefer locating resources relative to the repository root (one level up from utils).
    here = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.normpath(os.path.join(here, ".."))
    candidate = os.path.join(project_root, relative_path)
    return os.path.abspath(candidate)


def normalize_to_absolute_path(path: str) -> str:
    """Normalize relative paths to absolute paths from current working dir."""
    if not path:
        return path
    if os.path.isabs(path):
        return os.path.normpath(path)
    return os.path.normpath(os.path.abspath(path))
