from __future__ import annotations

from pathlib import Path, PurePath
from typing import Union, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from lightweight import Site


class SitePath:
    """An implementation of Path interface.
    File system operations performed on real_path; relative path is used for all other operations.

    `__str__` returns relative path representation.

    Changed defaults:
    - mkdir -- parents and exists_ok are made `True`.

    Added:
    - create -- create file with contents.
    """

    def __init__(self, path: Union[Path, str], site: Site):
        self.site = site
        self.relative_path = Path(path) if isinstance(path, str) else path

    @property
    def real_path(self):
        return self.site.out / self.relative_path

    @property
    def name(self):
        return self.relative_path.name

    @property
    def parts(self) -> Tuple[str, ...]:
        return self.relative_path.parts

    @property
    def parent(self) -> SitePath:
        return self.site.path(self.relative_path.parent)

    def absolute(self) -> Path:
        return self.real_path.absolute()

    def exists(self) -> bool:
        return self.real_path.exists()

    def mkdir(self, mode=0o777, parents=True, exist_ok=True):
        return self.real_path.mkdir(mode=mode, parents=parents, exist_ok=exist_ok)

    def __truediv__(self, other: Union[SitePath, PurePath]):
        other_path: PurePath
        if isinstance(other, SitePath):
            other_path = other.relative_path
        elif isinstance(other, PurePath):
            other_path = other
        else:
            raise ValueError(f'Cannot make a path with {other}')
        return self.site.path(self.relative_path / other_path)

    def __str__(self):
        return str(self.relative_path)

    def with_name(self, name: str) -> SitePath:
        return self.site.path(self.relative_path.with_name(name))

    def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
        return self.real_path.open(mode=mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline)

    def with_suffix(self, suffix: str) -> SitePath:
        return self.site.path(self.relative_path.with_suffix(suffix))

    def create(self, content: Union[str, bytes]) -> None:
        self.parent.mkdir()
        binary_mode = isinstance(content, bytes)
        with self.open('wb' if binary_mode else 'w') as f:
            f.write(content)
