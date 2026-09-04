from pathlib import Path
import time

from src.aia_qa.watcher import list_qa_files
from src.aia_qa.workflow import QAProcessResult, process_qa_instruction_file
from src.common.config import qa_paths


def run(in_dir: Path) -> list[Path]:
    return list_qa_files(in_dir)


def run_once(ai_root: Path | None = None) -> list[QAProcessResult]:
    runtime = qa_paths(ai_root)
    return [process_qa_instruction_file(file, runtime) for file in list_qa_files(runtime.in_dir)]


def run_forever(ai_root: Path | None = None, poll_interval_seconds: int = 5) -> None:
    while True:
        run_once(ai_root)
        time.sleep(poll_interval_seconds)


if __name__ == "__main__":
    run_forever(Path.home() / "AI")
