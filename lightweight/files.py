from glob import iglob
from pathlib import Path
from typing import Iterator


def create_file(path: Path, *, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w') as f:
        f.write(content)


def paths(path: str) -> Iterator[Path]:
    return iglob(path, recursive=True)


def strip_extension(file_name: str):
    return file_name.rsplit('.', 1)[0]
