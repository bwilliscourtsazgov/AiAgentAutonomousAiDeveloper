from dataclasses import dataclass
import os
from pathlib import Path

from src.aia_coder.markdown_parser import parse_instruction
from src.aia_coder.copilot_client import CopilotClient
from src.aia_coder.qa_instruction_writer import write_qa_instruction
from src.aia_coder.task_executor import TaskExecutor
from src.common.activity_log import append_event
from src.common.config import AgentPaths, ai_root_from_agent_paths
from src.common.fs_utils import ensure_agent_dirs, move_to_dir
from src.common.git_utils import (
    build_coder_branch_name,
    build_coder_commit_message,
    checkout_new_branch,
    commit_all_changes,
    ensure_repo_ready,
    push_branch,
)


@dataclass(slots=True)
class ProcessResult:
    instruction_name: str
    succeeded: bool
    message: str
    branch_name: str | None = None


def process_instruction(instruction_name: str, instruction_body: str, qa_output: Path) -> None:
    qa_content = (
        f"# QA Instructions\n\n"
        f"Validate implementation for: {instruction_name}\n\n"
        f"{instruction_body[:400]}"
    )
    write_qa_instruction(qa_output, qa_content)


def process_instruction_file(
    instruction_in_file: Path,
    coder_paths: AgentPaths,
    qa_in_dir: Path,
) -> ProcessResult:
    ai_root = ai_root_from_agent_paths(coder_paths)
    instruction_name = instruction_in_file.name
    ensure_agent_dirs(
        coder_paths.in_dir,
        coder_paths.processing_dir,
        coder_paths.success_dir,
        coder_paths.failure_dir,
        qa_in_dir,
    )

    append_event(ai_root, "AIAgentCoder", "lifecycle", instruction_name, "IN", {"path": str(instruction_in_file)})

    processing_file = move_to_dir(instruction_in_file, coder_paths.processing_dir)
    instruction_name = processing_file.name
    append_event(
        ai_root,
        "AIAgentCoder",
        "lifecycle",
        instruction_name,
        "PROCESSING",
        {"path": str(processing_file)},
    )
    branch_name = build_coder_branch_name(processing_file.name)

    try:
        parsed = parse_instruction(processing_file)
        repo_path = parsed.repo.local_path
        ensure_repo_ready(
            repo_path,
            parsed.repo.repo_url,
            parsed.repo.branch,
            parsed.repo.create_remote,
            parsed.repo.visibility,
        )
        append_event(
            ai_root,
            "AIAgentCoder",
            "git",
            instruction_name,
            "REPO_READY",
            {"repo_path": str(repo_path), "base_branch": parsed.repo.branch or ""},
        )
        checkout_new_branch(repo_path, branch_name)
        append_event(
            ai_root,
            "AIAgentCoder",
            "git",
            instruction_name,
            "CHECKOUT_NEW_BRANCH",
            {"branch": branch_name},
        )
        if os.environ.get("AI_BACKEND"):
            task = CopilotClient().ask_for_task(parsed.body)
            TaskExecutor().apply(repo_path, task)
            append_event(
                ai_root,
                "AIAgentCoder",
                "ai",
                instruction_name,
                "TASK_APPLIED",
                {"summary": task.summary, "changes": len(task.changes)},
            )
        qa_output = qa_in_dir / f"{processing_file.stem}_qa.md"
        process_instruction(processing_file.name, parsed.body, qa_output)
        append_event(
            ai_root,
            "AIAgentCoder",
            "handoff",
            instruction_name,
            "AIAgentQA_IN",
            {"qa_instruction_path": str(qa_output)},
        )
        move_to_dir(processing_file, coder_paths.success_dir)
        append_event(
            ai_root,
            "AIAgentCoder",
            "lifecycle",
            instruction_name,
            "SUCCESS",
            {"path": str(coder_paths.success_dir / instruction_name)},
        )
        commit_message = build_coder_commit_message(processing_file.name)
        commit_all_changes(repo_path, commit_message)
        append_event(
            ai_root,
            "AIAgentCoder",
            "git",
            instruction_name,
            "COMMIT",
            {"message": commit_message},
        )
        push_branch(repo_path, branch_name)
        append_event(
            ai_root,
            "AIAgentCoder",
            "git",
            instruction_name,
            "PUSH",
            {"branch": branch_name},
        )
        return ProcessResult(processing_file.name, True, "Processed successfully", branch_name)
    except Exception as exc:
        if processing_file.exists():
            move_to_dir(processing_file, coder_paths.failure_dir)

        failure_note = coder_paths.failure_dir / f"{processing_file.stem}.error.txt"
        failure_note.write_text(str(exc), encoding="utf-8")
        append_event(
            ai_root,
            "AIAgentCoder",
            "lifecycle",
            instruction_name,
            "FAILURE",
            {"path": str(coder_paths.failure_dir / instruction_name), "error": str(exc)},
        )
        return ProcessResult(processing_file.name, False, str(exc), branch_name)
