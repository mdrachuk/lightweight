from __future__ import annotations

from os import getcwd
from pathlib import Path
from shutil import rmtree
from typing import overload, Union, Optional
from urllib.parse import urlparse

from lightweight.content import Content, ContentCollection
from lightweight.content.collection import IncludedContent
from lightweight.content.copy import FileCopy, DirectoryCopy
from lightweight.errors import AbsolutePathIncluded, IncludedDuplicate
from lightweight.files import paths
from lightweight.path import Rendering, RenderPath


class Site(ContentCollection, Content):
    def __init__(self,
                 *,
                 url: Optional[str] = None,
                 title: Optional[str] = None):
        super().__init__([], self)
        self.title = title
        if url is not None:
            url_parts = urlparse(url)
            assert url_parts.scheme, 'Missing scheme in Site URL.'
        self.url = url

    @overload
    def include(self, path: str):
        """Include a file, a directory, or multiple files with a glob pattern."""

    @overload
    def include(self, path: str, content: Content):
        """Create a file at path with content."""

    def include(self, path: str, content: Content = None):
        cwd = getcwd()
        if path.startswith('/'):
            raise AbsolutePathIncluded()
        if content is None:
            contents = {str(path): file_or_dir(path) for path in paths(path)}
            if not len(contents):
                raise FileNotFoundError()
            for path, content in contents.items():
                self._include(path, content, cwd)
        else:
            self._include(path, content, cwd)

    def _include(self, path, content, cwd):
        if path in self:
            raise IncludedDuplicate()
        self.content.append(IncludedContent(path, content, cwd))

    def render(self, out: Union[str, Path] = 'out'):
        out = Path(out)
        if out.exists():
            rmtree(out)
        out.mkdir(parents=True, exist_ok=True)

        rendering = Rendering(out=out, site=self)
        rendering.perform()

    def write(self, path: RenderPath):
        rendering = Rendering(out=(path.ctx.out / path.relative_path).absolute(), site=self)
        rendering.perform()

    def __repr__(self):
        return f'<{type(self).__name__} title={self.title} url={self.url} at 0x{id(self):02x}>'


def file_or_dir(path: Path):
    return FileCopy(path) if path.is_file() else DirectoryCopy(path)
