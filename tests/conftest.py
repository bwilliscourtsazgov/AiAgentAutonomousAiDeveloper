import os

import pytest


@pytest.fixture(autouse=True)
def disable_live_ai_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AI_BACKEND", raising=False)
