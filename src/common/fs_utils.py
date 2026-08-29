from pathlib import Path


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def move_file(source: Path, destination: Path) -> None:
    ensure_dir(destination.parent)
    source.replace(destination)


def ensure_agent_dirs(*paths: Path) -> None:
    for path in paths:
        ensure_dir(path)


def move_to_dir(source: Path, destination_dir: Path) -> Path:
    ensure_dir(destination_dir)
    destination = destination_dir / source.name
    move_file(source, destination)
    return destination
