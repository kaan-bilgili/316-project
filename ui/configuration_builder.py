import sys

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
}


def _normalize_run_command(command):
    if sys.platform == "win32" and command.startswith("./"):
        return command[2:]
    return command


def config_to_prog_lang(config):
    if config.is_interpreted:
        return "Python (Interpreter)"
    if config.source_filename.endswith(".java"):
        return "Java (JDK)"
    return "C (GCC)"


def build_configuration(config_name, prog_lang, compiler_path, select_prog_lang_label):
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
