from pathlib import Path


def list_instruction_files(in_dir: Path) -> list[Path]:
    if not in_dir.exists():
        return []
    return sorted(in_dir.glob("*.md"))
