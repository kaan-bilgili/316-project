import os
import sys


def _dev_project_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, ".."))


def _frozen_base_dirs():
    """Candidate roots for bundled data files (PyInstaller onefile/onedir)."""
    dirs = []
    seen = set()

    def add(path):
        norm = os.path.normpath(path)
        if norm not in seen and os.path.isdir(norm):
            seen.add(norm)
            dirs.append(norm)

    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        add(meipass)

    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    add(exe_dir)
    add(os.path.join(exe_dir, "_internal"))

    return dirs


def iter_resource_paths(relative_path: str):
    """Yield candidate absolute paths for a bundled resource (most likely first)."""
    rel = relative_path.replace("/", os.sep)

    if getattr(sys, "frozen", False):
        yielded = set()
        for base in _frozen_base_dirs():
            candidate = os.path.normpath(os.path.join(base, rel))
            if candidate not in yielded:
                yielded.add(candidate)
                yield candidate
        return

    yield os.path.abspath(os.path.join(_dev_project_root(), rel))


def find_resource_path(relative_path: str) -> str | None:
    """Return the first existing file path for a resource, or None."""
    for candidate in iter_resource_paths(relative_path):
        if os.path.isfile(candidate):
            return candidate
    return None


def get_resource_path(relative_path: str) -> str:
    """Return an absolute path to a bundled resource (best candidate)."""
    found = find_resource_path(relative_path)
    if found:
        return found
    return next(iter_resource_paths(relative_path))


def find_resource_dir(relative_dir: str) -> str | None:
    """Return the first existing directory path for a bundled resource folder."""
    for candidate in iter_resource_paths(relative_dir):
        if os.path.isdir(candidate):
            return candidate
    return None


def get_user_data_dir() -> str:
    """Return a writable per-user folder (safe when installed under Program Files)."""
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
    else:
        base = os.environ.get(
            "XDG_DATA_HOME",
            os.path.join(os.path.expanduser("~"), ".local", "share"),
        )
    path = os.path.join(base, "IAE")
    os.makedirs(path, exist_ok=True)
    return path


def get_configurations_dir() -> str:
    """Writable configuration storage (not next to the installed executable)."""
    path = os.path.join(get_user_data_dir(), "configurations")
    os.makedirs(path, exist_ok=True)
    return path


def normalize_to_absolute_path(path: str) -> str:
    """Normalize relative paths to absolute paths from current working dir."""
    if not path:
        return path
    if os.path.isabs(path):
        return os.path.normpath(path)
    return os.path.normpath(os.path.abspath(path))
