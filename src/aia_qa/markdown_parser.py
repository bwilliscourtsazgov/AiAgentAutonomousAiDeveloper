from pathlib import Path


def read_test_instruction(markdown_file: Path) -> str:
    return markdown_file.read_text(encoding="utf-8")
