from pathlib import Path


def list_qa_files(in_dir: Path) -> list[Path]:
    return sorted(in_dir.glob("*.md"))
