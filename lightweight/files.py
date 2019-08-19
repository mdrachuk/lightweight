from dataclasses import dataclass
from os import scandir, DirEntry
from pathlib import Path
from typing import Iterator


def create_file(path: Path, *, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w') as f:
        f.write(content)


@dataclass(frozen=True)
class File:
    name: str
    path: str
    is_markdown: bool
    is_html: bool
    is_directory: bool


def directory(path: str) -> Iterator[File]:
    return (scan_file(f) for f in scandir(path))


def scan_file(f: DirEntry):
    is_file = f.is_file()
    return File(
        strip_extension(f.name),
        f.path,
        is_markdown=is_file and (f.name.endswith('.md') or f.name.endswith('.markdown')),
        is_html=is_file and f.name.endswith('.html'),
        is_directory=f.is_dir(),
    )


def strip_extension(file_name: str):
    return file_name.rsplit('.', 1)[0]
