from pathlib import Path

from src.common.models import ParsedInstruction, RepoSettings


_ALLOWED_REPO_KEYS = {"local_path", "repo_url", "branch"}


def read_instruction(markdown_file: Path) -> str:
    return markdown_file.read_text(encoding="utf-8")


def parse_instruction(markdown_file: Path) -> ParsedInstruction:
    content = read_instruction(markdown_file)
    metadata, body = _parse_yaml_front_matter(content)
    _validate_instruction_metadata(metadata)

    local_path = metadata.get("local_path")

    repo = RepoSettings(
        local_path=Path(local_path).expanduser(),
        repo_url=metadata.get("repo_url"),
        branch=metadata.get("branch"),
    )
    return ParsedInstruction(repo=repo, body=body)


def _validate_instruction_metadata(metadata: dict[str, str]) -> None:
    unknown_keys = [key for key in metadata if key not in _ALLOWED_REPO_KEYS]
    if unknown_keys:
        raise ValueError(
            "Invalid instruction metadata key(s): "
            f"{', '.join(sorted(unknown_keys))}. "
            f"Allowed keys are: {', '.join(sorted(_ALLOWED_REPO_KEYS))}."
        )

    local_path = metadata.get("local_path", "").strip()
    if not local_path:
        raise ValueError("Instruction metadata must include non-empty 'local_path'.")

    repo_url = metadata.get("repo_url")
    if repo_url is not None and not repo_url.strip():
        raise ValueError("If provided, 'repo_url' must be non-empty.")

    branch = metadata.get("branch")
    if branch is not None and not branch.strip():
        raise ValueError("If provided, 'branch' must be non-empty.")


def _parse_yaml_front_matter(content: str) -> tuple[dict[str, str], str]:
    if not content.startswith("---\n") and not content.startswith("---\r\n"):
        raise ValueError("Instruction file must start with YAML front matter.")

    lines = content.splitlines()
    end_index = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break

    if end_index is None:
        raise ValueError("YAML front matter is not terminated with '---'.")

    metadata: dict[str, str] = {}
    for line in lines[1:end_index]:
        raw = line.strip()
        if not raw or raw.startswith("#"):
            continue
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")

    body = "\n".join(lines[end_index + 1 :]).lstrip("\n")
    return metadata, body
