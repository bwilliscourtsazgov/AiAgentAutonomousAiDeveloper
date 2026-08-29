from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AgentPaths:
    in_dir: Path
    processing_dir: Path
    success_dir: Path
    failure_dir: Path


def default_ai_root() -> Path:
    return Path.home() / "AI"


def agent_paths(agent_folder: str, ai_root: Path | None = None) -> AgentPaths:
    root = ai_root or default_ai_root()
    base = root / agent_folder
    return AgentPaths(
        in_dir=base / "IN",
        processing_dir=base / "PROCESSING",
        success_dir=base / "SUCCESS",
        failure_dir=base / "FAILURE",
    )


def coder_paths(ai_root: Path | None = None) -> AgentPaths:
    return agent_paths("AIAgentCoder", ai_root)


def qa_paths(ai_root: Path | None = None) -> AgentPaths:
    return agent_paths("AIAgentQA", ai_root)
