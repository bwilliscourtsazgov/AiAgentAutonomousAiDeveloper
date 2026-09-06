from pathlib import Path

from src.common.models import FileChange, TaskResponse


_ALLOWED_OPERATIONS = {"create", "update", "delete"}


class TaskExecutor:
    def apply(self, repository: Path, task: TaskResponse) -> None:
        root = repository.resolve()
        for change in task.changes:
            target = self._safe_path(root, change.path)
            if change.operation not in _ALLOWED_OPERATIONS:
                raise ValueError(f"Unsupported file operation: {change.operation}")
            if change.operation in {"create", "update"}:
                if change.content is None:
                    raise ValueError(f"Content is required for {change.operation}: {change.path}")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(change.content, encoding="utf-8")
            elif target.exists():
                if target.is_dir():
                    raise ValueError(f"Cannot delete directory: {change.path}")
                target.unlink()

    @staticmethod
    def _safe_path(root: Path, relative_path: str) -> Path:
        candidate = (root / relative_path).resolve()
        if candidate != root and root not in candidate.parents:
            raise ValueError(f"File path escapes repository: {relative_path}")
        return candidate
