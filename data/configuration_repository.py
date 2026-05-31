import json
import os
import shutil
import tempfile
from typing import List, Optional

from model.configuration import Configuration
from utils.path_utils import find_resource_dir, get_configurations_dir


class ConfigurationRepository:

    def __init__(self, configurations_dir: str | None = None):
        """Initializes the repository with a folder for JSON configuration files."""
        self.configurations_dir = configurations_dir or get_configurations_dir()
        self._seed_default_configurations()

    def _seed_default_configurations(self) -> None:
        bundled_dir = find_resource_dir("configurations")
        if not bundled_dir:
            legacy_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..", "configurations"
            )
            legacy_dir = os.path.normpath(legacy_dir)
            if os.path.isdir(legacy_dir):
                bundled_dir = legacy_dir
        if not bundled_dir:
            return

        for filename in os.listdir(bundled_dir):
            if not filename.endswith(".json"):
                continue
            destination = os.path.join(self.configurations_dir, filename)
            if not os.path.exists(destination):
                shutil.copy2(os.path.join(bundled_dir, filename), destination)

    def save(self, configuration: Configuration) -> None:
        """Saves a configuration as a JSON file."""
        configuration.validate()
        self._validate_name(configuration.name)
        os.makedirs(self.configurations_dir, exist_ok=True)

        path = self._get_path(configuration.name)
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.configurations_dir,
                delete=False,
                suffix=".tmp",
            ) as file:
                json.dump(configuration.to_dict(), file, indent=4)
                temp_path = file.name

            os.replace(temp_path, path)
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    def update(self, old_name: str, configuration: Configuration) -> None:
        """Updates an existing configuration. Handles name changes."""
        self._validate_name(old_name)
        configuration.validate()
        self._validate_name(configuration.name)

        if old_name != configuration.name:
            self.save(configuration)
            self.delete(old_name)
            return

        self.save(configuration)

    def load(self, name: str) -> Optional[Configuration]:
        """Loads a configuration by name. Returns None if it does not exist."""
        self._validate_name(name)
        path = self._get_path(name)

        if not os.path.exists(path):
            return None

        with open(path, "r", encoding="utf-8") as file:
            return Configuration.from_dict(json.load(file))

    def exists(self, name: str) -> bool:
        """Returns True if a configuration exists with the given name."""
        self._validate_name(name)
        return os.path.exists(self._get_path(name))

    def delete(self, name: str) -> bool:
        """Deletes a configuration by name. Returns True if a file was deleted."""
        self._validate_name(name)
        path = self._get_path(name)

        if not os.path.exists(path):
            return False

        os.remove(path)
        return True

    def export_to_file(self, name: str, destination_path: str) -> None:
        """Exports a configuration to a specified file path."""
        self._validate_name(name)
        config = self.load(name)
        if config is None:
            raise FileNotFoundError(f"Configuration '{name}' not found.")
        with open(destination_path, "w", encoding="utf-8") as file:
            json.dump(config.to_dict(), file, indent=4)

    def import_from_file(self, source_path: str) -> Configuration:
        """Imports a configuration from a specified file path."""
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"File not found: {source_path}")
        with open(source_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        config = Configuration.from_dict(data)
        self.save(config)
        return config

    def load_all(self) -> List[Configuration]:
        """Loads all JSON configurations from the repository folder."""
        if not os.path.isdir(self.configurations_dir):
            return []

        configurations = []
        for filename in sorted(os.listdir(self.configurations_dir)):
            if filename.endswith(".json"):
                path = os.path.join(self.configurations_dir, filename)
                try:
                    with open(path, "r", encoding="utf-8") as file:
                        configurations.append(Configuration.from_dict(json.load(file)))
                except (OSError, json.JSONDecodeError, ValueError):
                    continue

        return configurations

    def _get_path(self, name: str) -> str:
        filename = f"{name}.json"
        return os.path.join(self.configurations_dir, filename)

    def _validate_name(self, name: str) -> None:
        if not isinstance(name, str):
            raise ValueError("Configuration name must be text.")
        if not name.strip():
            raise ValueError("Configuration name is required.")
        if os.path.basename(name) != name:
            raise ValueError("Configuration name cannot contain path separators.")
