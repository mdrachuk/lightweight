from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path, PurePath
from typing import TYPE_CHECKING, Union, Tuple, TextIO, BinaryIO, Callable

if TYPE_CHECKING:
    from lightweight import Site, Content

UrlFactory = Callable[[str], str]


@dataclass(frozen=True)
class GenTask:
    path: GenPath
    content: Content
    cwd: str


class GenContext:
    site: Site
    out: Path
    tasks: Tuple[GenTask, ...]

    def __init__(self, out: Path, site: Site):
        self.out = out
        self.site = site

    def path(self, p: Union[Path, str]) -> GenPath:
        return GenPath(Path(p), self.out, lambda location: self.site / location)


@dataclass(frozen=True)
class GenPath:
    """An implementation of Path interface.
    File system operations performed on real_path; relative path is used for all other operations.

    `__str__` returns relative path representation.

    Changed defaults:
    - mkdir -- parents and exists_ok are made `True`.

    Added:
    - create -- create file with contents.
    """
    relative_path: Path
    out: Path
    url_factory: UrlFactory

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
        return replace(self, relative_path=self.relative_path.parent)

    @property
    def suffix(self) -> str:
        return self.relative_path.suffix

    @property
    def url(self) -> str:
        return self.url_factory(self.location)  # type: ignore # Invalid self argument mypy error

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
        return replace(self, relative_path=self.relative_path / other_path)

    def __str__(self):
        return str(self.relative_path)

    def with_name(self, name: str) -> GenPath:
        return replace(self, relative_path=self.relative_path.with_name(name))

    def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None) -> Union[TextIO, BinaryIO]:
        return self.real_path.open(mode=mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline)

    def with_suffix(self, suffix: str) -> GenPath:
        return replace(self, relative_path=self.relative_path.with_suffix(suffix))

    def create(self, content: Union[str, bytes]) -> None:
        self.parent.mkdir()
        binary_mode = isinstance(content, bytes)
        with self.open('xb' if binary_mode else 'w') as f:
            f.write(content)  # type: ignore
