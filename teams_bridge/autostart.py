"""Autostart application after user logs in."""

import getpass
import os
from pathlib import Path
import plistlib


class Autostart:
    """Autostart application after user logs in."""

    def __init__(
        self, base_path: str = f"/Users/{getpass.getuser()}/Library/LaunchAgents"
    ):
        """Initialise autostart."""
        self.base_path: str = base_path

    def enable(self, name: str, program_arguments: list[str]):
        """Enable autostart for the application under the provided name."""
        options = {"Label": name, "ProgramArguments": program_arguments}
        # Create path if it doesn't exist.
        Path(self.base_path).mkdir(parents=True, exist_ok=True)
        with open(self.get_path_for_application(name), "wb") as file:
            plistlib.dump(options, file)

    def disable(self, name: str):
        """Disable autostart for the application under the provided name."""
        path = self.get_path_for_application(name)
        if os.path.exists(path):
            os.remove(path)
        else:
            raise FileNotFoundError("Unable to find file %s", path)

    def is_enabled(self, name: str) -> bool:
        """Check if autostart for the application under the provided name is enabled."""
        return os.path.exists(self.get_path_for_application(name))

    def get_path_for_application(self, name: str) -> str:
        """Get the path for the application."""
        return f"{self.base_path}/{name}.plist"
