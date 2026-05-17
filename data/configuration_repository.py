import json
import os
from typing import List, Optional

from model.configuration import Configuration


class ConfigurationRepository:

    def __init__(self, configurations_dir: str = "configurations"):
        """Initializes the repository with a folder for JSON configuration files."""
        self.configurations_dir = configurations_dir

    def save(self, configuration: Configuration) -> None:
        """Saves a configuration as a JSON file."""
        configuration.validate()
        self._validate_name(configuration.name)
        os.makedirs(self.configurations_dir, exist_ok=True)

        with open(self._get_path(configuration.name), "w", encoding="utf-8") as file:
            json.dump(configuration.to_dict(), file, indent=4)

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

    def load_all(self) -> List[Configuration]:
        """Loads all JSON configurations from the repository folder."""
        if not os.path.isdir(self.configurations_dir):
            return []

        configurations = []

        for filename in os.listdir(self.configurations_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.configurations_dir, filename)

                with open(path, "r", encoding="utf-8") as file:
                    configurations.append(Configuration.from_dict(json.load(file)))

        return configurations

    def _get_path(self, name: str) -> str:
        filename = f"{name}.json"
        return os.path.join(self.configurations_dir, filename)

    def _validate_name(self, name: str) -> None:
        if not name.strip():
            raise ValueError("Configuration name is required.")
        if os.path.basename(name) != name:
            raise ValueError("Configuration name cannot contain path separators.")
