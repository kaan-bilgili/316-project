import sys
from dataclasses import dataclass


def _normalize_run_command(command: str) -> str:
    if sys.platform == "win32" and command.startswith("./"):
        return command[2:]
    return command


DEFAULT_RUN_COMMAND = "main.exe" if sys.platform == "win32" else "./main.exe"


@dataclass
class Configuration:
    name: str
    compiler_path: str = "gcc"
    source_filename: str = "main.c"
    compiler_args: str = "-o main.exe"
    run_command: str = DEFAULT_RUN_COMMAND
    is_interpreted: bool = False

    def validate(self) -> None:
        """Checks the required fields for this prototype configuration."""
        required_fields = (
            ("name", self.name, "Configuration name"),
            ("compiler_path", self.compiler_path, "Compiler path"),
            ("source_filename", self.source_filename, "Source filename"),
            ("run_command", self.run_command, "Run command"),
        )

        for _field_name, value, label in required_fields:
            if not isinstance(value, str):
                raise ValueError(f"{label} must be text.")
            if not value.strip():
                raise ValueError(f"{label} is required.")

        if "/" in self.name or "\\" in self.name:
            raise ValueError("Configuration name cannot contain path separators.")
        if not isinstance(self.compiler_args, str):
            raise ValueError("Compiler args must be text.")
        if not isinstance(self.is_interpreted, bool):
            raise ValueError("Interpreted flag must be boolean.")

    def to_dict(self) -> dict:
        """Converts the configuration to a dict for JSON storage."""
        self.validate()

        return {
            "name": self.name,
            "compiler_path": self.compiler_path,
            "source_filename": self.source_filename,
            "compiler_args": self.compiler_args,
            "run_command": self.run_command,
            "is_interpreted": self.is_interpreted,
        }

    @staticmethod
    def from_dict(data: dict) -> "Configuration":
        """Creates a Configuration instance from a JSON dict."""
        if not isinstance(data, dict):
            raise ValueError("Configuration data must be a JSON object.")

        configuration = Configuration(
            name=Configuration._read_text(data, "name", ""),
            compiler_path=Configuration._read_text(data, "compiler_path", "gcc"),
            source_filename=Configuration._read_text(
                data, "source_filename", "main.c"
            ),
            compiler_args=Configuration._read_text(
                data, "compiler_args", "-o main.exe"
            ),
            run_command=_normalize_run_command(
                Configuration._read_text(data, "run_command", DEFAULT_RUN_COMMAND)
            ),
            is_interpreted=Configuration._read_bool(
                data, "is_interpreted", False
            ),
        )
        configuration.validate()
        return configuration

    @staticmethod
    def _read_text(data: dict, key: str, default: str) -> str:
        value = data.get(key, default)
        if value is None:
            return default
        if not isinstance(value, str):
            raise ValueError(f"Configuration field '{key}' must be text.")
        return value

    @staticmethod
    def _read_bool(data: dict, key: str, default: bool) -> bool:
        value = data.get(key, default)
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in ("true", "1", "yes"):
                return True
            if normalized in ("false", "0", "no"):
                return False
        raise ValueError(f"Configuration field '{key}' must be boolean.")
