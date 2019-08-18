from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import scandir, DirEntry
from pathlib import Path
from shutil import rmtree, copytree, copy
from typing import Iterator, overload

import misaka
from jinja2 import Environment, FileSystemLoader


class Content(ABC):

    @abstractmethod
    def render(self) -> None:
        pass


@dataclass
class Copy(Content):
    source: Path
    target: Path

    def render(self) -> None:
        if self.source.is_dir():
            copytree(str(self.source), str(self.target))
        else:
            copy(str(self.source), str(self.target))


@dataclass
class Create(Content):
    path: Path
    content: str

    def render(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('w') as f:
            f.write(self.content)


class Site:

    def __init__(self, out: str = 'out'):
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.out = Path(out)
        self.commands = []

    @overload
    def include(self, path: str):
        """Include file or directory."""
        ...

    @overload
    def include(self, path: str, content: str):
        """Create a file at path with content."""
        ...

    def include(self, path: str, content: str = None):
        path = Path(path)
        target = self.out.joinpath(path)
        if content is None:
            command = Copy(path, target)
        else:
            command = Create(target, content)
        self.commands.append(command)

    def template(self, name):
        return self.env.get_template(name)

    def render(self):
        if self.out.exists():
            rmtree(self.out)
        self.out.mkdir()
        [cmd.render() for cmd in self.commands]


def markdown(path: str):
    contents = open(path).read()
    return misaka.html(contents)


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
