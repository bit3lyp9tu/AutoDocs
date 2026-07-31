
import subprocess

from src.schemas.config_model import ConfigSchema


class GitMaster:
    def __init__(self, config: ConfigSchema) -> None:
        self.config = config

    def diff(self):
        diff = subprocess.check_output(
            ["git", "diff", "--cached"],
            text=True,
        )
        return diff
