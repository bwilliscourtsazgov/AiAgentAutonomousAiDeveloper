from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class InstructionTask:
    name: str
    source_path: Path
    processing_path: Path


@dataclass(slots=True)
class RepoSettings:
    local_path: Path
    repo_url: str | None = None
    branch: str | None = None
    create_remote: bool = False
    visibility: str = "private"


@dataclass(slots=True)
class ParsedInstruction:
    repo: RepoSettings
    body: str


@dataclass(slots=True)
class AISettings:
    backend: str
    api_key: str
    model: str
    endpoint: str | None = None
    api_version: str | None = None
    deployment: str | None = None


@dataclass(slots=True)
class FileChange:
    operation: str
    path: str
    content: str | None = None


@dataclass(slots=True)
class TaskResponse:
    summary: str
    changes: list[FileChange]
    validation_commands: list[str]
