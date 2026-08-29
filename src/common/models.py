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


@dataclass(slots=True)
class ParsedInstruction:
    repo: RepoSettings
    body: str
