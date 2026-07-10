
import subprocess

from src.config_model import Config


class GitMaster:
    def __init__(self, config: Config) -> None:
        self.config = config

    def diff(self):
        # git commit -am '<<autodocs-auto>>'

        diff = subprocess.check_output(
            ["git", "diff"],
            text=True,
        )
        return diff
