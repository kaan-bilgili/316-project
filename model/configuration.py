from dataclasses import dataclass


@dataclass
class Configuration:
    name: str
    compiler_path: str = "gcc"
    source_filename: str = "main.c"
    compiler_args: str = "-o main.exe"
    run_command: str = "./main.exe"
    is_interpreted: bool = False

    def to_dict(self) -> dict:
        """Converts the configuration to a dict for JSON storage."""
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
        return Configuration(
            name=data["name"],
            compiler_path=data.get("compiler_path", "gcc"),
            source_filename=data.get("source_filename", "main.c"),
            compiler_args=data.get("compiler_args", "-o main.exe"),
            run_command=data.get("run_command", "./main.exe"),
            is_interpreted=data.get("is_interpreted", False),
        )