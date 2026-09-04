from dataclasses import dataclass
from pathlib import Path

from src.aia_qa.markdown_parser import read_test_instruction
from src.common.activity_log import append_event
from src.common.config import AgentPaths, ai_root_from_agent_paths
from src.common.fs_utils import ensure_agent_dirs, move_to_dir


@dataclass(slots=True)
class QAProcessResult:
    instruction_name: str
    succeeded: bool
    message: str


def process_qa_instruction(markdown_file: Path) -> str:
    return read_test_instruction(markdown_file)


def process_qa_instruction_file(instruction_in_file: Path, qa_paths: AgentPaths) -> QAProcessResult:
    ai_root = ai_root_from_agent_paths(qa_paths)
    instruction_name = instruction_in_file.name
    ensure_agent_dirs(
        qa_paths.in_dir,
        qa_paths.processing_dir,
        qa_paths.success_dir,
        qa_paths.failure_dir,
    )
    append_event(ai_root, "AIAgentQA", "lifecycle", instruction_name, "IN", {"path": str(instruction_in_file)})
    processing_file = move_to_dir(instruction_in_file, qa_paths.processing_dir)
    append_event(
        ai_root,
        "AIAgentQA",
        "lifecycle",
        instruction_name,
        "PROCESSING",
        {"path": str(processing_file)},
    )
    try:
        process_qa_instruction(processing_file)
        move_to_dir(processing_file, qa_paths.success_dir)
        append_event(
            ai_root,
            "AIAgentQA",
            "lifecycle",
            instruction_name,
            "SUCCESS",
            {"path": str(qa_paths.success_dir / instruction_name)},
        )
        return QAProcessResult(instruction_name, True, "Processed successfully")
    except Exception as exc:
        if processing_file.exists():
            move_to_dir(processing_file, qa_paths.failure_dir)
        append_event(
            ai_root,
            "AIAgentQA",
            "lifecycle",
            instruction_name,
            "FAILURE",
            {"path": str(qa_paths.failure_dir / instruction_name), "error": str(exc)},
        )
        return QAProcessResult(instruction_name, False, str(exc))
