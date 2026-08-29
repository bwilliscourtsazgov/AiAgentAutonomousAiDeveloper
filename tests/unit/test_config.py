from pathlib import Path

from src.common.config import coder_paths, qa_paths


def test_coder_paths_uses_ai_root(tmp_path: Path) -> None:
    paths = coder_paths(tmp_path)

    assert paths.in_dir == tmp_path / "AIAgentCoder" / "IN"
    assert paths.processing_dir == tmp_path / "AIAgentCoder" / "PROCESSING"
    assert paths.success_dir == tmp_path / "AIAgentCoder" / "SUCCESS"
    assert paths.failure_dir == tmp_path / "AIAgentCoder" / "FAILURE"


def test_qa_paths_uses_ai_root(tmp_path: Path) -> None:
    paths = qa_paths(tmp_path)

    assert paths.in_dir == tmp_path / "AIAgentQA" / "IN"
