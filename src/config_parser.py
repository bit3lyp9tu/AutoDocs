import json
import yaml
from typing import IO, Callable, ClassVar, Generic, TypeVar

from pydantic import BaseModel
from pydantic_core import ValidationError

from src.schemas.config_model import ConfigSchema
from src.file_factory import FileWriter
from src.schemas.setup_schema import SetupSchema


class ConfigError(Exception):
    pass

T = TypeVar("T", bound=BaseModel)

class Config(Generic[T]):
    schema: type[T]
    loader: ClassVar[Callable[[IO[str]], dict]]
    dumper: ClassVar[Callable[[dict], str]]

    default_path = ""

    def __init__(self, config_path: str | None = None) -> None:
        if config_path:
            self.config_path = config_path
        else:
            if self.default_path:
                self.config_path = self.default_path
            else:
                raise ValueError("No config path defined")

        with open(self.config_path, 'r') as f:
            data = type(self).loader(f)

        try:
            self.config: T = self.schema.model_validate(data)
        except ValidationError as ve:
            raise ConfigError(
                f"Invalid configuration in '{self.config_path} as {self.schema}'"
            ) from ve

    def createFile(self, path):
        FileWriter(path).write(
            type(self).dumper(self.config.model_dump())
        )

class YAMLConfig(Config[ConfigSchema]):
    schema = ConfigSchema
    loader = yaml.safe_load
    dumper = lambda data: yaml.dump(
        data,
        default_flow_style=False,
        indent=4,
    )
    default_path = "autodocs.yaml"

class JSONConfig(Config[SetupSchema]):
    schema = SetupSchema
    loader = json.load
    dumper = lambda data: json.dumps(
        data,
        indent=4,
    )
