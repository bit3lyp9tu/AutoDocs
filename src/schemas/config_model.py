
from pathlib import Path
from typing import Self

from pydantic import BaseModel, field_validator, model_validator


from pathlib import Path

def find_project_root(start: Path) -> Path:
    for path in (start.resolve(), *start.resolve().parents):
        if (path / "pyproject.toml").exists():
            return path
    raise FileNotFoundError("Could not find project root.")

class RendererNotFoundError(Exception):
    pass

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

class LLMStatus(BaseModel):
    type: str
    pre_check_connection: bool = True
    show_model_response_time: bool = True
    show_model_status: bool = True
    url: str

class LLMService(BaseModel):
    api: API
    status: LLMStatus
    alt_models: list[str] = []

class PlantUML(BaseModel):
    renderer_path: str

    @field_validator("renderer_path")
    @classmethod
    def validate_path(cls, value: str | None) -> str | None:
        if value is not None:
            PROJECT_ROOT = find_project_root(Path(__file__))
            path = Path(PROJECT_ROOT / value)
            if not path.exists() or not path.is_file() or not value.endswith('.jar'):
                raise ValueError(f"Renderer path [{path}] not found")
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

    # @field_validator("file_path")
    # @classmethod
    # def validate_path(cls, value: str | None) -> str | None:
    #     if value is not None:
    #         path = Path(value)
    #         if not path.exists():
    #             raise ValueError(f"Path does not exist: {value}")
    #         if not path.is_file():
    #             raise ValueError(f"Not a file: {value}")
    #     return value

class Prompts(BaseModel):
    path: str
    header_path: str = ""
    footer_path: str = ""
    # TODO file validation???

class LLM_Log(BaseModel):
    add_thinking_response: bool = True

class Logs(BaseModel):
    llm_log: LLM_Log

class AutoDocs(BaseModel):
    files_ignore_path: str
    model: str
    prompts: Prompts
    plantuml: PlantUML
    valid_diagrams: ValidDiagrams
    logs: Logs

class GitCommit(BaseModel):
    allow_auto_msg: bool = True
    sysprompt: SysPrompt
    vim_examination: bool = True
    llm_model: str
    timeout: int = 600

class Git(BaseModel):
    commit: GitCommit

class ConfigSchema(BaseModel):
    llm_service: LLMService
    autodocs: AutoDocs
    git: Git
