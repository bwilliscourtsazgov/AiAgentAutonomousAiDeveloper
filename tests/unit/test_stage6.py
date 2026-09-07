from pathlib import Path

import pytest

from src.aia_coder.copilot_client import CopilotClient
from src.aia_coder.task_executor import TaskExecutor
from src.common.config import load_ai_settings
from src.common.models import AISettings, FileChange, TaskResponse


def test_load_openai_settings() -> None:
    settings = load_ai_settings({"AI_BACKEND": "openai", "OPENAI_API_KEY": "key", "OPENAI_MODEL": "model"})
    assert settings.backend == "openai"
    assert settings.model == "model"


def test_load_azure_settings() -> None:
    settings = load_ai_settings({"AI_BACKEND": "azure", "AZURE_OPENAI_API_KEY": "key", "AZURE_OPENAI_ENDPOINT": "https://example", "AZURE_OPENAI_API_VERSION": "2024-10-21", "AZURE_OPENAI_DEPLOYMENT": "deployment"})
    assert settings.backend == "azure"
    assert settings.model == "deployment"


def test_client_parses_structured_response() -> None:
    client = CopilotClient(AISettings("openai", "key", "model"), client=None)
    client.ask = lambda prompt: '{"summary":"done","changes":[{"operation":"create","path":"a.txt","content":"x"}],"validation_commands":[]}'
    result = client.ask_for_task("task")
    assert result.changes[0].path == "a.txt"


def test_client_rejects_non_list_changes() -> None:
    client = CopilotClient(AISettings("openai", "key", "model"), client=None)
    client.ask = lambda prompt: '{"summary":"done","changes":"none","validation_commands":[]}'
    with pytest.raises(ValueError, match="changes must be a list"):
        client.ask_for_task("task")


def test_executor_applies_changes(tmp_path: Path) -> None:
    task = TaskResponse("done", [FileChange("create", "nested/a.txt", "hello")], [])
    TaskExecutor().apply(tmp_path, task)
    assert (tmp_path / "nested" / "a.txt").read_text() == "hello"


def test_executor_rejects_path_escape(tmp_path: Path) -> None:
    task = TaskResponse("bad", [FileChange("create", "../outside.txt", "bad")], [])
    with pytest.raises(ValueError, match="escapes repository"):
        TaskExecutor().apply(tmp_path, task)
