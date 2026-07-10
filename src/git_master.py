
from src.config_model import Config


class GitMaster:
    def __init__(self, config: Config) -> None:
        self.config = config

    def diff(self):
        # git diff HEAD~1
        pass
