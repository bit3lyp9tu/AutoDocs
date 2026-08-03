from pathlib import Path

from pydantic import BaseModel, field_validator

class MetaData(BaseModel):
    model_name: str = ""
    temperature: float = -1.0
    max_tokens: int = -1
    input_tokens: int = -1
    output_tokens: int = -1
    total_tokens: int = -1
    response_time_seconds: float = -1.0
    error_msg: str = ""

class Session(BaseModel):
    meta_data: MetaData
    content: list[str] = []

class SetupSchema(BaseModel):
    config_path: str = "autodocs.yaml"
    root_path: str
    autodocs_path: str = ".autodocs"
    resolved_prompt: str
    docs_header: str = ""
    docs_footer: str = ""
    sessions: dict[str, Session]

    @field_validator("config_path")
    @classmethod
    def validate_config(cls, value: str) -> str:
        path = Path(value).expanduser()
        if not path.exists():
            raise ValueError(f"Path does not exist: {value}")
        if not path.is_file():
            raise ValueError(f"Not a file: {value}")
        if not str(path).endswith(".yaml"):
            raise ValueError(f"File [{value}] is not a .yaml file")

        return value

    @field_validator("root_path", "autodocs_path")
    @classmethod
    def validate_dirs(cls, value: str) -> str:
        path = Path(value).expanduser()
        if not path.exists():
            raise ValueError(f"Path does not exist: {value}")
        if not path.is_dir():
            raise ValueError(f"Not a directory: {value}")

        return value
