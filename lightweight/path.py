from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Union, Tuple, TYPE_CHECKING

from .files import directory

if TYPE_CHECKING:
    from lightweight import Site, Content


@dataclass(frozen=True)
class RenderTask:
    path: RenderPath
    content: Content
    cwd: str

    def perform(self):
        with directory(self.cwd):
            self.content.write(self.path)


class Rendering:
    site: Site
    out: Path

    paths: Tuple[RenderPath, ...]
    contents: Tuple[Content, ...]

    def __init__(self, out: Path, site: Site):
        self.site = site
        self.out = out
        self.tasks = [
            RenderTask(self.path(c.path), c.content, c.cwd)
            for c in site.content
        ]

    def path(self, p: Union[Path, str]) -> RenderPath:
        return RenderPath(p, self)

    def perform(self):
        [task.perform() for task in self.tasks]


class RenderPath:
    """An implementation of Path interface.
    File system operations performed on real_path; relative path is used for all other operations.

    `__str__` returns relative path representation.

    Changed defaults:
    - mkdir -- parents and exists_ok are made `True`.

    Added:
    - create -- create file with contents.
    """

    def __init__(self, path: Union[Path, str], ctx: Rendering):
        self.ctx = ctx
        self.relative_path = Path(path) if isinstance(path, str) else path

    @property
    def real_path(self):
        return self.ctx.out / self.relative_path

    @property
    def name(self):
        return self.relative_path.name

    @property
    def parts(self) -> Tuple[str, ...]:
        return self.relative_path.parts

    @property
    def parent(self) -> RenderPath:
        return self.ctx.path(self.relative_path.parent)

    @property
    def suffix(self) -> str:
        return self.relative_path.suffix

    @property
    def url(self) -> str:
        return f'{self.ctx.site.url}/{self.location}'  # TODO:mdrachuk:10.12.2019: subsite urls

    @property
    def location(self) -> str:
        return str(self.with_suffix('') if self.suffix == '.html' else self)

    def absolute(self) -> Path:
        return self.real_path.absolute()

    def exists(self) -> bool:
        return self.real_path.exists()

    def mkdir(self, mode=0o777, parents=True, exist_ok=True):
        return self.real_path.mkdir(mode=mode, parents=parents, exist_ok=exist_ok)

    def __truediv__(self, other: Union[RenderPath, PurePath, str]):
        other_path: Union[PurePath, str]
        if isinstance(other, RenderPath):
            other_path = other.relative_path
        elif isinstance(other, PurePath) or isinstance(other, str):
            other_path = other
        else:
            raise ValueError(f'Cannot make a path with {other}')
        return self.ctx.path(self.relative_path / other_path)

    def __str__(self):
        return str(self.relative_path)

    def with_name(self, name: str) -> RenderPath:
        return self.ctx.path(self.relative_path.with_name(name))

    def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
        return self.real_path.open(mode=mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline)

    def with_suffix(self, suffix: str) -> RenderPath:
        return self.ctx.path(self.relative_path.with_suffix(suffix))

    def create(self, content: Union[str, bytes]) -> None:
        self.parent.mkdir()
        binary_mode = isinstance(content, bytes)
        with self.open('wb' if binary_mode else 'w') as f:
            f.write(content)
