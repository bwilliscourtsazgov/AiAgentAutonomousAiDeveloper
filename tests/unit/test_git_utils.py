from datetime import datetime

from src.common.git_utils import (
    build_coder_branch_name,
    build_coder_commit_message,
    slugify_instruction_name,
)


def test_slugify_instruction_name() -> None:
    assert slugify_instruction_name("Login Feature.md") == "login-feature"


def test_build_coder_branch_name() -> None:
    now = datetime(2026, 1, 2, 3, 4, 5)
    assert build_coder_branch_name("Login Feature.md", now) == "agent/coder/20260102030405-login-feature"


def test_build_coder_commit_message() -> None:
    assert build_coder_commit_message("loginFeature.md") == "feat: process instruction loginFeature.md"
