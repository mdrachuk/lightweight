from __future__ import annotations

from pathlib import Path
from shutil import rmtree
from typing import overload, Union, Optional, Dict
from urllib.parse import urlparse

from lightweight.content import Content, ContentCollection
from lightweight.content.copy import FileCopy, DirectoryCopy
from lightweight.errors import NoSourcePath
from lightweight.files import paths
from lightweight.path import SitePath


class Site(ContentCollection):
    content: Dict[Path, Content]

    def __init__(self, *,
                 url: str,
                 out: Union[str, Path] = 'out',
                 title: Optional[str] = None):
        super().__init__({})
        url_parts = urlparse(url)
        assert url_parts.scheme, 'Missing scheme in Site URL.'
        self.title = title or url_parts.netloc
        self.url = url
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
            contents = {path: _file_or_dir(path) for path in paths(pattern_or_path)}
            if not len(contents):
                raise FileNotFoundError()
            self.content.update(contents)
        else:
            path = Path(pattern_or_path)
            self.content[path] = content

    def path(self, p: Union[Path, str]) -> SitePath:
        return SitePath(p, self)

    def render(self):
        if self.out.exists():
            rmtree(self.out)
        self.out.mkdir(parents=True, exist_ok=True)
        [content.render(self.path(p)) for p, content in self.content.items()]


def _file_or_dir(path: Path):
    return FileCopy(path) if path.is_file() else DirectoryCopy(path)
