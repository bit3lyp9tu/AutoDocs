from contextlib import contextmanager
import json
import yaml
from typing import IO, Callable, ClassVar, Generic, TypeVar

from pydantic import BaseModel
from pydantic_core import ValidationError

from libs.llm_api_toolcollection.src.config_parser import ConfigBase, YAMLConfig

from src.schemas.config_model import ConfigSchema
from src.file_factory import FileWriter
from src.schemas.setup_schema import SetupSchema


class JSONConfig(ConfigBase[SetupSchema]):
    schema = SetupSchema
    loader = json.load
    dumper = lambda data: json.dumps(
        data,
        indent=4,
    )
