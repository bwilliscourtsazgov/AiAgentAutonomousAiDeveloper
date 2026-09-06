from pathlib import Path
import subprocess
from datetime import datetime, timezone
import re
from urllib.parse import urlparse


def run_git(repo_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_path,
        text=True,
        check=True,
        capture_output=True,
    )


def run_gh(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", *args],
        cwd=cwd,
        text=True,
        check=True,
        capture_output=True,
    )


def github_repository_name(repo_url: str) -> str:
    normalized = repo_url.removesuffix(".git")
    if normalized.startswith("git@github.com:"):
        return normalized.removeprefix("git@github.com:")

    parsed = urlparse(normalized)
    if parsed.hostname != "github.com":
        raise ValueError("repo_url must point to github.com when create_remote is true.")
    return parsed.path.strip("/")


def create_github_repository(repo_path: Path, repo_url: str, visibility: str = "private") -> None:
    repository_name = github_repository_name(repo_url)
    if not repository_name or "/" not in repository_name:
        raise ValueError("repo_url must include a GitHub owner and repository name.")

    run_gh(
        "repo",
        "create",
        repository_name,
        f"--{visibility}",
        "--source",
        str(repo_path),
        "--remote",
        "origin",
        "--push",
    )


def run_git_global(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        check=True,
        capture_output=True,
    )


def slugify_instruction_name(instruction_name: str) -> str:
    stem = Path(instruction_name).stem.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    return slug or "task"


def build_coder_branch_name(instruction_name: str, now: datetime | None = None) -> str:
    timestamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%d%H%M%S")
    slug = slugify_instruction_name(instruction_name)
    return f"agent/coder/{timestamp}-{slug}"


def build_coder_commit_message(instruction_name: str) -> str:
    return f"feat: process instruction {instruction_name}"


def checkout_new_branch(repo_path: Path, branch_name: str) -> None:
    run_git(repo_path, "checkout", "-b", branch_name)


def commit_all_changes(repo_path: Path, message: str) -> None:
    run_git(repo_path, "add", "-A")
    run_git(repo_path, "commit", "-m", message)


def push_branch(repo_path: Path, branch_name: str) -> None:
    run_git(repo_path, "push", "-u", "origin", branch_name)


def is_git_repository(path: Path) -> bool:
    return (path / ".git").exists()


def ensure_repo_ready(
    local_path: Path,
    repo_url: str | None = None,
    branch: str | None = None,
    create_remote: bool = False,
    visibility: str = "private",
) -> None:
    remote_created = False
    if not local_path.exists():
        local_path.parent.mkdir(parents=True, exist_ok=True)
        if repo_url and not create_remote:
            run_git_global("clone", repo_url, str(local_path))
        else:
            local_path.mkdir(parents=True, exist_ok=True)
            run_git_global("init", "-b", "main", cwd=local_path)

    if not is_git_repository(local_path):
        run_git_global("init", "-b", "main", cwd=local_path)

    if create_remote and repo_url and not _has_commits(local_path):
        run_git(local_path, "checkout", "-B", "main")
        run_git(local_path, "commit", "--allow-empty", "-m", "chore: initialize repository")

    if create_remote and repo_url and not _has_remote(local_path, "origin"):
        create_github_repository(local_path, repo_url, visibility)
        remote_created = True

    base_branch = branch or "main"
    if repo_url and _has_remote(local_path, "origin") and not remote_created:
        if remote_branch_exists(local_path, "origin", base_branch):
            run_git(local_path, "pull", "origin", base_branch)

    if branch:
        checkout_or_create_branch(local_path, branch)


def checkout_or_create_branch(repo_path: Path, branch_name: str) -> None:
    try:
        run_git(repo_path, "checkout", branch_name)
    except subprocess.CalledProcessError:
        run_git(repo_path, "checkout", "-b", branch_name)


def _has_remote(repo_path: Path, remote_name: str) -> bool:
    try:
        result = run_git(repo_path, "remote")
    except subprocess.CalledProcessError:
        return False
    remotes = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    return remote_name in remotes


def remote_branch_exists(repo_path: Path, remote_name: str, branch_name: str) -> bool:
    try:
        run_git(repo_path, "ls-remote", "--exit-code", "--heads", remote_name, branch_name)
    except subprocess.CalledProcessError as exc:
        if exc.returncode == 2:
            return False
        raise RuntimeError(
            f"Unable to query remote branch '{remote_name}/{branch_name}'. "
            "Check GitHub authentication and repository access."
        ) from exc
    return True


def _has_commits(repo_path: Path) -> bool:
    try:
        run_git(repo_path, "rev-parse", "--verify", "HEAD")
    except subprocess.CalledProcessError:
        return False
    return True
