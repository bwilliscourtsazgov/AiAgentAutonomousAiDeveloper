from pathlib import Path

from src.aia_qa.markdown_parser import read_test_instruction


def process_qa_instruction(markdown_file: Path) -> str:
    return read_test_instruction(markdown_file)
