from dataclasses import dataclass
import os
from pathlib import Path

from src.common.models import AISettings


@dataclass(slots=True)
class AgentPaths:
    in_dir: Path
    processing_dir: Path
    success_dir: Path
    failure_dir: Path


def default_ai_root() -> Path:
    return Path.home() / "AI"


def logs_dir(ai_root: Path | None = None) -> Path:
    return (ai_root or default_ai_root()) / "Logs"


def coder_log_dir(ai_root: Path | None = None) -> Path:
    return (ai_root or default_ai_root()) / "AIAgentCoder" / "Log"


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


def ai_root_from_agent_paths(paths: AgentPaths) -> Path:
    return paths.in_dir.parents[1]


def load_ai_settings(environ: dict[str, str] | None = None) -> AISettings:
    values = environ or os.environ
    backend = values.get("AI_BACKEND", "").strip().lower()
    if backend not in {"openai", "azure"}:
        raise ValueError("AI_BACKEND must be either 'openai' or 'azure'.")

    if backend == "openai":
        api_key = values.get("OPENAI_API_KEY", "").strip()
        model = values.get("OPENAI_MODEL", "").strip()
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when AI_BACKEND=openai.")
        if not model:
            raise ValueError("OPENAI_MODEL is required when AI_BACKEND=openai.")
        return AISettings(backend=backend, api_key=api_key, model=model)

    api_key = values.get("AZURE_OPENAI_API_KEY", "").strip()
    endpoint = values.get("AZURE_OPENAI_ENDPOINT", "").strip()
    api_version = values.get("AZURE_OPENAI_API_VERSION", "").strip()
    deployment = values.get("AZURE_OPENAI_DEPLOYMENT", "").strip()
    missing = [
        name
        for name, value in {
            "AZURE_OPENAI_API_KEY": api_key,
            "AZURE_OPENAI_ENDPOINT": endpoint,
            "AZURE_OPENAI_API_VERSION": api_version,
            "AZURE_OPENAI_DEPLOYMENT": deployment,
        }.items()
        if not value
    ]
    if missing:
        raise ValueError(f"Missing Azure OpenAI configuration: {', '.join(missing)}.")
    return AISettings(
        backend=backend,
        api_key=api_key,
        model=deployment,
        endpoint=endpoint,
        api_version=api_version,
        deployment=deployment,
    )
