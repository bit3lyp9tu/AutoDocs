from typing import Generic, TypeVar

from pydantic import BaseModel
from pydantic_core import ValidationError
import yaml

from src.schemas.config_model import Config as ConfigSchema
from src.file_factory import FileWriter
from src.schemas.setup_schema import Setup as SetupSchema


class ConfigError(Exception):
    pass

T = TypeVar("T", bound=BaseModel)
class Config(Generic[T]):
    schema: type[T]
    default_path = ""

    def __init__(self, config_path: str | None = None) -> None:
        self.config_path = config_path or self.default_path

        with open(self.config_path, 'r') as f:
            data = yaml.safe_load(f)

        try:
            self.config: T = self.schema.model_validate(data)
        except ValidationError as ve:
            raise ConfigError(
                f"Invalid configuration in '{self.config_path}'"
            ) from ve

    def createFile(self, path):
        FileWriter(path).write(
            content=yaml.dump(
                self.config.model_dump(),
                default_flow_style=False,
                indent=4
            )
        )

class YAMLConfig(Config[ConfigSchema]):
    schema = ConfigSchema
    default_path = "autodocs.yaml"

class JSONConfig(Config[SetupSchema]):
    schema = SetupSchema
