from pathlib import Path

from pydantic import BaseModel, field_validator


class Setup(BaseModel):
    config_path: str = "autodocs.yaml"
    root_path: str
    autodocs_path: str = ".autodocs"
    resolved_prompt: str
    docs_header: str
    sessions: dict[str, list[str]]

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
