from pathlib import Path
from typing import Self

from pydantic import BaseModel, field_validator, model_validator

from pathlib import Path

from libs.llm_api_toolcollection.src.schemas.config_schema import LLMService, Logs, Prompts, SysPrompt


def find_project_root(start: Path) -> Path:
    for path in (start.resolve(), *start.resolve().parents):
        if (path / "pyproject.toml").exists():
            return path
    raise FileNotFoundError("Could not find project root.")

class RendererNotFoundError(Exception):
    pass

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
