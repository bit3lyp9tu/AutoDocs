from contextlib import contextmanager
import json

from llm_api_toolcollection.config_parser import ConfigBase, YAMLConfig

from src.schemas.setup_schema import SetupSchema


class JSONConfig(ConfigBase[SetupSchema]):
    schema = SetupSchema
    loader = json.load
    dumper = lambda data: json.dumps(
        data,
        indent=4,
    )
