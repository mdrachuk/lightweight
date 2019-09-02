from __future__ import annotations

from pathlib import Path, PurePath
from shutil import rmtree
from typing import overload, Union, Dict, Optional, Mapping, Any, Tuple

from lightweight.content import Content
from lightweight.content.copy import FileCopy, DirectoryCopy
from lightweight.errors import NoSourcePath
from lightweight.files import paths


class SitePath:

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
    def parts(self) -> Tuple[str]:
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


class ContentCollection:

    def __init__(self, content: Mapping[SitePath, Content]):
        self.content = dict(content)

    def __getitem__(self, path_part: str) -> ContentAtPath:
        return ContentAtPath(Path(path_part), {
            path: content
            for path, content in self.content.items()
            if path.parts[0] == path_part
        }, self)


class Site(ContentCollection):

    def __init__(self, out: Union[str, Path] = 'out'):
        super().__init__({})
        self.out = Path(out)

    @overload
    def include(self, arg: str):
        """Include a file or directory."""

    @overload
    def include(self, arg: Union[str, Path], content: Content):
        """Create a file at path with content."""

    @overload
    def include(self, arg: Content):
        """"""

    def include(self, arg: Union[str, Path, Content], content: Content = None):
        if isinstance(arg, Content):
            source_path = getattr(arg, 'source_path', None)  # type: Optional[Path]
            if source_path is None:
                raise NoSourcePath()
            arg, content = source_path, arg  # type: ignore

        pattern_or_path = arg  # type: Union[str, Path]
        if content is None:
            contents = {self.path(path): _file_or_dir(path) for path in paths(pattern_or_path)}
            if not len(contents):
                raise FileNotFoundError()
            self.content.update(contents)
        else:
            path = self.path(pattern_or_path)
            self.content[path] = content

    def path(self, p: Union[Path, str]) -> SitePath:
        return SitePath(p, self)

    def render(self):
        if self.out.exists():
            rmtree(self.out)
        self.out.mkdir(parents=True, exist_ok=True)
        [content.render(path) for path, content in self.content.items()]


def _file_or_dir(path: Path):
    return FileCopy(path) if path.is_file() else DirectoryCopy(path)


class ContentAtPath(ContentCollection):

    def __init__(self, path: SitePath, content: Dict[SitePath, Content], source: Any):
        super().__init__(content)
        self.rel_path = path
        self.base_size = len(self.rel_path.parts)

        self.id = self.rel_path
        self.title = path
        self.author_name = getattr(source, 'author_name', None)
        self.author_email = getattr(source, 'author_email', None)

    def __getitem__(self, path_part: str):
        return ContentAtPath(Path(path_part), {
            path: content
            for path, content in self.content.items()
            if path.parts[self.base_size] == path_part
        }, self)
