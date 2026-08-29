from pathlib import Path

from src.common.fs_utils import ensure_dir, move_to_dir


def test_ensure_dir_creates_path(tmp_path: Path) -> None:
    target = tmp_path / "a" / "b"
    ensure_dir(target)
    assert target.exists()


def test_move_to_dir_moves_file(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    destination_dir = tmp_path / "destination"
    source.write_text("content", encoding="utf-8")

    moved = move_to_dir(source, destination_dir)

    assert moved == destination_dir / "source.md"
    assert moved.exists()
    assert not source.exists()
