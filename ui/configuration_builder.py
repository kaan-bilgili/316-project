import sys
from typing import Optional

from model.configuration import Configuration

PROG_LANG_PRESETS = {
    "C (GCC)": {
        "source_filename": "main.c",
        "compiler_args": "-o main.exe",
        "run_command": "main.exe" if sys.platform == "win32" else "./main.exe",
        "is_interpreted": False,
    },
    "Java (JDK)": {
        "source_filename": "Main.java",
        "compiler_args": "",
        "run_command": "java Main",
        "is_interpreted": False,
    },
    "Python (Interpreter)": {
        "source_filename": "main.py",
        "compiler_args": "",
        "run_command": "python main.py",
        "is_interpreted": True,
    },
    "C++ (G++)": {
        "source_filename": "main.cpp",
        "compiler_args": "-o main.exe",
        "run_command": "main.exe" if sys.platform == "win32" else "./main.exe",
        "is_interpreted": False,
    },
}


def _normalize_run_command(command: str) -> str:
    if sys.platform == "win32" and command.startswith("./"):
        return command[2:]
    return command


def config_to_prog_lang(config: Configuration) -> str:
    source_filename = config.source_filename.lower()
    if config.is_interpreted and source_filename.endswith(".py"):
        return "Python (Interpreter)"
    if not config.is_interpreted and source_filename.endswith(".java"):
        return "Java (JDK)"
    if not config.is_interpreted and source_filename.endswith(".cpp"):
        return "C++ (G++)"
    if not config.is_interpreted and source_filename.endswith(".c"):
        return "C (GCC)"
    raise ValueError(
        f"Unsupported configuration source file: {config.source_filename}"
    )


def build_configuration(
    config_name: str,
    prog_lang: str,
    compiler_path: Optional[str],
    select_prog_lang_label: str,
) -> Optional[Configuration]:
    if prog_lang == select_prog_lang_label or prog_lang not in PROG_LANG_PRESETS:
        return None

    preset = PROG_LANG_PRESETS[prog_lang]
    compiler_path = (compiler_path or "").strip()
    if not compiler_path:
        return None

    run_command = _normalize_run_command(preset["run_command"])
    if preset["is_interpreted"]:
        run_command = f'"{compiler_path}" {preset["source_filename"]}'

    return Configuration(
        name=config_name,
        compiler_path=compiler_path,
        source_filename=preset["source_filename"],
        compiler_args=preset["compiler_args"],
        run_command=run_command,
        is_interpreted=preset["is_interpreted"],
    )
