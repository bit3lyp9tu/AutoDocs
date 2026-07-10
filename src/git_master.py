
import subprocess

from src.config_model import Config


class GitMaster:
    def __init__(self, config: Config) -> None:
        self.config = config

    def diff(self):
        diff = subprocess.check_output(
            ["git", "diff", "--cached"],
            text=True,
        )
        return diff
