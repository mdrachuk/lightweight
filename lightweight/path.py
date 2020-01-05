from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Union, Tuple, TYPE_CHECKING, TextIO, BinaryIO

from .files import directory

if TYPE_CHECKING:
    from lightweight import Site, Content


@dataclass(frozen=True)
class GenTask:
    path: GenPath
    content: Content
    cwd: str

    def perform(self, ctx: GenContext):
        with directory(self.cwd):
            self.content.write(self.path, ctx)


class GenContext:
    site: Site
    out: Path

    paths: Tuple[GenPath, ...]
    contents: Tuple[Content, ...]

    def __init__(self, out: Path, site: Site):
        self.site = site
        self.out = out
        self.tasks = [GenTask(self.path(c.path), c.content, c.cwd) for c in site.content]

    def path(self, p: Union[Path, str]) -> GenPath:
        return GenPath(p, self.out, lambda location: self.site / location)

    def perform(self):
        [task.perform(self) for task in self.tasks]


class GenPath:
    """An implementation of Path interface.
    File system operations performed on real_path; relative path is used for all other operations.

    `__str__` returns relative path representation.

    Changed defaults:
    - mkdir -- parents and exists_ok are made `True`.

    Added:
    - create -- create file with contents.
    """

    def __init__(self, path: Union[Path, str], out: Path, url_factory):
        self.out = out
        self.url_factory = url_factory
        self.relative_path = Path(path) if isinstance(path, str) else path

    @property
    def real_path(self):
        return self.out / self.relative_path

    @property
    def name(self):
        return self.relative_path.name

    @property
    def parts(self) -> Tuple[str, ...]:
        return self.relative_path.parts

    @property
    def parent(self) -> GenPath:
        return self.copy(path=self.relative_path.parent)

    @property
    def suffix(self) -> str:
        return self.relative_path.suffix

    @property
    def url(self) -> str:
        return self.url_factory(self.location)

    @property
    def location(self) -> str:
        return str(self.with_suffix('') if self.suffix == '.html' else self)

    def absolute(self) -> Path:
        return self.real_path.absolute()

    def exists(self) -> bool:
        return self.real_path.exists()

    def mkdir(self, mode=0o777, parents=True, exist_ok=True):
        return self.real_path.mkdir(mode=mode, parents=parents, exist_ok=exist_ok)

    def __truediv__(self, other: Union[GenPath, PurePath, str]):
        other_path: Union[PurePath, str]
        if isinstance(other, GenPath):
            other_path = other.relative_path
        elif isinstance(other, PurePath) or isinstance(other, str):
            other_path = other
        else:
            raise ValueError(f'Cannot make a path with {other}')
        return self.copy(path=self.relative_path / other_path)

    def __str__(self):
        return str(self.relative_path)

    def with_name(self, name: str) -> GenPath:
        return self.copy(path=self.relative_path.with_name(name))

    def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None) -> Union[TextIO, BinaryIO]:
        return self.real_path.open(mode=mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline)

    def with_suffix(self, suffix: str) -> GenPath:
        return self.copy(path=self.relative_path.with_suffix(suffix))

    def create(self, content: Union[str, bytes]) -> None:
        self.parent.mkdir()
        binary_mode = isinstance(content, bytes)
        with self.open('xb' if binary_mode else 'w') as f:
            f.write(content)  # type: ignore

    def copy(self, *, path: Path = None):
        if path is None:
            path = self.relative_path
        return GenPath(path, self.out, self.url_factory)
