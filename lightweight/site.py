from __future__ import annotations

from pathlib import Path
from shutil import rmtree
from typing import overload, Union, Optional, Dict
from urllib.parse import urlparse

from lightweight.content import Content, ContentCollection
from lightweight.content.copy import FileCopy, DirectoryCopy
from lightweight.errors import NoSourcePath
from lightweight.files import paths
from lightweight.path import Rendering, RenderPath


class Site(ContentCollection, Content):
    content: Dict[str, Content]

    def __init__(self,
                 *,
                 url: Optional[str] = None,
                 title: Optional[str] = None):
        super().__init__({}, self)
        self.title = title
        if url is not None:
            url_parts = urlparse(url)
            assert url_parts.scheme, 'Missing scheme in Site URL.'
        self.url = url

    @overload
    def include(self, arg: str):
        """Include a file or directory."""

    @overload
    def include(self, arg: str, content: Content):
        """Create a file at path with content."""

    @overload
    def include(self, arg: Content):
        """"""

    @overload
    def include(self, arg: str, content: Site):
        """Include all of site contents in provided the directory."""

    def include(self, arg: Union[str, Content], content: Union[Content, str] = None):
        if isinstance(arg, Content):
            source_path = getattr(arg, 'path', None)  # type: Optional[Path]
            if source_path is None:
                raise NoSourcePath()
            arg, content = str(source_path), arg  # type: ignore

        pattern_or_path = arg  # type: str
        if pattern_or_path.startswith('/'):
            pattern_or_path = pattern_or_path[1:]
        if content is None:
            contents = {path: file_or_dir(path) for path in paths(pattern_or_path)}
            if not len(contents):
                raise FileNotFoundError()
            self.content.update(contents)
        else:
            self.content[pattern_or_path] = content

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


def file_or_dir(path: Path):
    return FileCopy(path) if path.is_file() else DirectoryCopy(path)
