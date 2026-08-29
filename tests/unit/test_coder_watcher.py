from pathlib import Path

from src.aia_coder.watcher import list_instruction_files


def test_list_instruction_files_returns_empty_for_missing_dir(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    assert list_instruction_files(missing) == []


def test_list_instruction_files_reads_markdown_only(tmp_path: Path) -> None:
    in_dir = tmp_path / "IN"
    in_dir.mkdir(parents=True, exist_ok=True)
    (in_dir / "a.md").write_text("a", encoding="utf-8")
    (in_dir / "b.txt").write_text("b", encoding="utf-8")

    files = list_instruction_files(in_dir)
    assert [file.name for file in files] == ["a.md"]
