
from pathlib import Path
from typing import Self

from pydantic import BaseModel, field_validator, model_validator


class API(BaseModel):
    base_url: str
    key_value: str | None = None
    key_location: str | None = None
    request_delay_seconds: int = 5

    @model_validator(mode="after")
    def validate_key_present(self) -> Self:
        if self.key_value is None and self.key_location is None:
            raise ValueError("Either 'key_value' or 'key_location' must be provided.")
        return self

    @field_validator("key_location")
    @classmethod
    def validate_path(cls, value: str | None) -> str | None:
        if value is not None:
            path = Path(value).expanduser()
            if not path.exists():
                raise ValueError(f"Path does not exist: {value}")
            if not path.is_file():
                raise ValueError(f"Not a file: {value}")
        return value

class LLMService(BaseModel):
    api: API


class PlantUML(BaseModel):
    renderer_path: str
    auto_render: bool = True

    @field_validator("renderer_path")
    @classmethod
    def validate_path(cls, value: str | None) -> str | None:
        if value is not None:
            path = Path(value)
            if not path.exists():
                raise ValueError(f"Path does not exist: {value}")
            if not path.is_file() or not value.endswith('.jar'):
                raise ValueError(f"Not a .jar file: {value}")
        return value

class ValidDiagrams(BaseModel):
    umls: list[str] = []
    non_umls: list[str] = []

    @model_validator(mode="after")
    def validate_list_size(self) -> Self:
        if len(self.umls) + len(self.non_umls) == 0:
            raise ValueError("Either 'umls' or 'non_umls' must contain at least one element.")
        return self

class SysPrompt(BaseModel):
    file_path: str
    # content: str

    @field_validator("file_path")
    @classmethod
    def validate_path(cls, value: str | None) -> str | None:
        if value is not None:
            path = Path(value)
            if not path.exists():
                raise ValueError(f"Path does not exist: {value}")
            if not path.is_file():
                raise ValueError(f"Not a file: {value}")
        return value

class AutoDocs(BaseModel):
    plantuml: PlantUML
    valid_diagrams: ValidDiagrams
    sysprompt: SysPrompt

class GitCommit(BaseModel):
    allow_auto_msg: bool = True
    sysprompt: SysPrompt
    vim_examination: bool = True
    llm_model: str

class Git(BaseModel):
    commit: GitCommit

class Config(BaseModel):
    llm_service: LLMService
    autodocs: AutoDocs
    git: Git
