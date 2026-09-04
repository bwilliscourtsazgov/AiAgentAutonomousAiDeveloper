from pathlib import Path

from src.aia_qa.workflow import process_qa_instruction, process_qa_instruction_file
from src.common.config import AgentPaths


def test_process_qa_instruction_reads_markdown(tmp_path: Path) -> None:
    qa = tmp_path / "qa.md"
    qa.write_text("Run tests", encoding="utf-8")

    assert process_qa_instruction(qa) == "Run tests"


def test_process_qa_instruction_file_logs_lifecycle(tmp_path: Path) -> None:
    qa_paths = AgentPaths(
        in_dir=tmp_path / "AIAgentQA" / "IN",
        processing_dir=tmp_path / "AIAgentQA" / "PROCESSING",
        success_dir=tmp_path / "AIAgentQA" / "SUCCESS",
        failure_dir=tmp_path / "AIAgentQA" / "FAILURE",
    )
    qa_paths.in_dir.mkdir(parents=True, exist_ok=True)
    instruction = qa_paths.in_dir / "qa-task.md"
    instruction.write_text("Run tests", encoding="utf-8")

    result = process_qa_instruction_file(instruction, qa_paths)

    assert result.succeeded is True
    assert (qa_paths.success_dir / instruction.name).exists()
    html_file = next((tmp_path / "AIAgentCoder" / "Log").glob("Log_*.html"))
    html = html_file.read_text(encoding="utf-8")
    assert ">IN</td>" in html
    assert ">PROCESSING</td>" in html
    assert ">SUCCESS</td>" in html
