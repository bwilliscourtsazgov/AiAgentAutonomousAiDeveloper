from datetime import datetime
import subprocess

import pytest

from src.common.git_utils import (
    build_coder_branch_name,
    build_coder_commit_message,
    create_github_repository,
    ensure_repo_ready,
    github_repository_name,
    remote_branch_exists,
    slugify_instruction_name,
)


def test_slugify_instruction_name() -> None:
    assert slugify_instruction_name("Login Feature.md") == "login-feature"


def test_build_coder_branch_name() -> None:
    now = datetime(2026, 1, 2, 3, 4, 5)
    assert build_coder_branch_name("Login Feature.md", now) == "agent/coder/20260102030405-login-feature"


def test_build_coder_commit_message() -> None:
    assert build_coder_commit_message("loginFeature.md") == "feat: process instruction loginFeature.md"


def test_github_repository_name_supports_https_and_ssh_urls() -> None:
    assert github_repository_name("https://github.com/org/HelloWorld.git") == "org/HelloWorld"
    assert github_repository_name("git@github.com:org/HelloWorld.git") == "org/HelloWorld"


def test_create_github_repository_pushes_source(monkeypatch, tmp_path) -> None:
    calls: list[tuple[str, ...]] = []
    monkeypatch.setattr(
        "src.common.git_utils.run_gh",
        lambda *args, cwd=None: calls.append(args),
    )

    create_github_repository(
        tmp_path,
        "https://github.com/org/HelloWorld.git",
        "private",
    )

    assert calls == [
        (
            "repo",
            "create",
            "org/HelloWorld",
            "--private",
            "--source",
            str(tmp_path),
            "--remote",
            "origin",
            "--push",
        )
    ]


def test_ensure_repo_ready_bootstraps_main_before_remote_creation(monkeypatch, tmp_path) -> None:
    global_calls: list[tuple[str, ...]] = []
    local_calls: list[tuple[str, ...]] = []

    monkeypatch.setattr(
        "src.common.git_utils.run_git_global",
        lambda *args, cwd=None: global_calls.append(args),
    )
    monkeypatch.setattr(
        "src.common.git_utils.run_git",
        lambda path, *args: local_calls.append(args),
    )
    monkeypatch.setattr("src.common.git_utils._has_remote", lambda *args: False)
    monkeypatch.setattr("src.common.git_utils._has_commits", lambda *args: False)
    monkeypatch.setattr("src.common.git_utils.create_github_repository", lambda *args: None)

    ensure_repo_ready(
        tmp_path / "new-repo",
        "https://github.com/org/HelloWorld.git",
        create_remote=True,
    )

    assert ("init", "-b", "main") in global_calls
    assert ("checkout", "-B", "main") in local_calls
    assert ("commit", "--allow-empty", "-m", "chore: initialize repository") in local_calls


def test_remote_branch_exists_returns_false_for_missing_branch(monkeypatch, tmp_path) -> None:
    def missing_branch(*args):
        raise subprocess.CalledProcessError(2, args)

    monkeypatch.setattr("src.common.git_utils.run_git", missing_branch)

    assert remote_branch_exists(tmp_path, "origin", "main") is False


def test_remote_branch_exists_reports_access_failure(monkeypatch, tmp_path) -> None:
    def access_failure(*args):
        raise subprocess.CalledProcessError(128, args)

    monkeypatch.setattr("src.common.git_utils.run_git", access_failure)

    with pytest.raises(RuntimeError, match="authentication"):
        remote_branch_exists(tmp_path, "origin", "main")
