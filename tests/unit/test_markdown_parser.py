from pathlib import Path
import pytest

from src.aia_coder.markdown_parser import parse_instruction, read_instruction


def test_read_instruction(tmp_path: Path) -> None:
    file_path = tmp_path / "task.md"
    file_path.write_text("# Task", encoding="utf-8")

    assert read_instruction(file_path) == "# Task"


def test_parse_instruction_reads_yaml_front_matter(tmp_path: Path) -> None:
    file_path = tmp_path / "task.md"
    file_path.write_text(
        "---\n"
        f"local_path: {tmp_path / 'target-repo'}\n"
        "repo_url: https://github.com/example/repo.git\n"
        "branch: develop\n"
        "create_remote: true\n"
        "visibility: public\n"
        "---\n"
        "Implement feature X\n",
        encoding="utf-8",
    )

    parsed = parse_instruction(file_path)

    assert parsed.repo.local_path == (tmp_path / "target-repo")
    assert parsed.repo.repo_url == "https://github.com/example/repo.git"
    assert parsed.repo.branch == "develop"
    assert parsed.repo.create_remote is True
    assert parsed.repo.visibility == "public"
    assert parsed.body == "Implement feature X"


def test_parse_instruction_rejects_unknown_yaml_keys(tmp_path: Path) -> None:
    file_path = tmp_path / "task.md"
    file_path.write_text(
        "---\n"
        f"local_path: {tmp_path / 'target-repo'}\n"
        "unexpected_key: value\n"
        "---\n"
        "Task body",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid instruction metadata key"):
        parse_instruction(file_path)


def test_parse_instruction_requires_non_empty_local_path(tmp_path: Path) -> None:
    file_path = tmp_path / "task.md"
    file_path.write_text(
        "---\n"
        "local_path: \n"
        "---\n"
        "Task body",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="non-empty 'local_path'"):
        parse_instruction(file_path)


def test_parse_instruction_rejects_remote_creation_without_url(tmp_path: Path) -> None:
    file_path = tmp_path / "task.md"
    file_path.write_text(
        "---\n"
        f"local_path: {tmp_path / 'target-repo'}\n"
        "create_remote: true\n"
        "---\n"
        "Task body",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="repo_url.*create_remote"):
        parse_instruction(file_path)
