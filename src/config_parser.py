import yaml

from src.config_model import Config


class YAMLConfig():
    def __init__(self, config_path="autodocs.yaml") -> None:
        self.config_path = config_path
        with open(self.config_path, 'r') as f:
            data = yaml.safe_load(f)

        self.config = Config.model_validate(data)
