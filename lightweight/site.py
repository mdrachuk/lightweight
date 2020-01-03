from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from os import getcwd
from pathlib import Path
from shutil import rmtree
from typing import overload, Union, Optional, Collection, Iterator, List, Set
from urllib.parse import urlparse, urljoin

from lightweight.content.content import Content
from lightweight.content.copy import FileCopy, DirectoryCopy
from lightweight.empty import Empty, empty
from lightweight.errors import AbsolutePathIncluded, IncludedDuplicate
from lightweight.files import paths
from lightweight.path import Rendering, RenderPath


class Site(Content):
    url: str
    content: List[IncludedContent]
    title: Optional[str]
    icon_url: Optional[str]
    logo_url: Optional[str]
    description: Optional[str]
    authors: Set[Author]
    language: Optional[str]
    copyright: Optional[str]
    updated: Optional[datetime]

    def __init__(
            self,
            url: str,
            *,
            content: Collection[IncludedContent] = None,
            title: Optional[str] = None,
            icon_url: Optional[str] = None,
            logo_url: Optional[str] = None,
            description: Optional[str] = None,
            author_name: Optional[str] = None,
            author_email: Optional[str] = None,
            authors: Collection[Author] = None,
            language: Optional[str] = None,
            copyright: Optional[str] = None,
            updated: Optional[datetime] = None,
    ):
        url_parts = urlparse(url)
        assert url_parts.scheme, 'Missing scheme in Site URL.'
        self.url = url
        self.content = [] if not content else list(content)
        self.title = title
        self.icon_url = icon_url
        self.logo_url = logo_url
        self.description = description
        self.author_name = author_name
        self.author_email = author_email
        authors = set() if authors is None else set(authors)
        if author_name or author_email:
            authors |= {Author(author_name, author_email)}
        self.authors = authors
        self.language = language
        self.copyright = copyright
        self.updated = updated

    def copy(
            self,
            url: Union[str, Empty] = empty,
            content: Union[Collection[IncludedContent], Empty] = empty,
            title: Union[Optional[str], Empty] = empty,
            icon_url: Union[Optional[str], Empty] = empty,
            description: Union[Optional[str], Empty] = empty,
            author_name: Union[Optional[str], Empty] = empty,
            author_email: Union[Optional[str], Empty] = empty,
            language: Union[Optional[str], Empty] = empty,
            copyright: Union[Optional[str], Empty] = empty,
            updated: Union[Optional[datetime], Empty] = empty,
    ) -> Site:
        return Site(
            url=url if url is not empty else self.url,  # type: ignore
            content=content if content is not empty else self.content,  # type: ignore
            title=title if title is not empty else self.title,  # type: ignore
            icon_url=icon_url if icon_url is not empty else self.icon_url,  # type: ignore
            description=description if description is not empty else self.description,  # type: ignore
            author_name=author_name if author_name is not empty else self.author_name,  # type: ignore
            author_email=author_email if author_email is not empty else self.author_email,  # type: ignore
            language=language if language is not empty else self.language,  # type: ignore
            copyright=copyright if copyright is not empty else self.copyright,  # type: ignore
            updated=updated if updated is not empty else self.updated,  # type: ignore
        )

    @overload
    def include(self, path: str):
        """Include a file, a directory, or multiple files with a glob pattern."""

    @overload
    def include(self, path: str, content: Content):
        """Create a file at path with content."""

    @overload
    def include(self, path: str, content: str):
        """Create a file at path with contents of a file at content path."""

    def include(self, path: str, content: Union[Content, str, None] = None):
        cwd = getcwd()
        if path.startswith('/'):
            raise AbsolutePathIncluded()
        if content is None:
            contents = {str(path): file_or_dir(path) for path in paths(path)}
            if not len(contents):
                raise FileNotFoundError()
            [self._include(path, content_, cwd) for path, content_ in contents.items()]
        elif isinstance(content, Content):
            self._include(path, content, cwd)
        elif isinstance(content, str):
            source = Path(content)
            if not source.exists():
                raise FileNotFoundError()
            self._include(path, file_or_dir(source), cwd)
        else:
            raise Exception(ValueError('Content, str, or None types are accepted as include parameter'))

    def _include(self, path: str, content: Content, cwd: str):
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

    def __truediv__(self, location: str):
        return urljoin(self.url, location)

    def __getitem__(self, path: str) -> Site:
        """Get a collection of content included at provided path.

            :Example:
            >>> site = Site(url='http://example.org', ...) # site is a collection of content

            >>> site.include('index.html', <index>)
            >>> site.include('posts/1', <post-1>)
            >>> site.include('posts/2', <post-2>)
            >>> site.include('posts/3', <post-3>)
            >>> site.include('static', <static>)

            >>> posts = site['posts']
            >>> assert posts.url is 'http://example.org/posts'
            >>> assert <post-1> in posts
            >>> assert <post-2> in posts
            >>> assert <post-3> in posts
            >>> assert <static> not in posts
        """
        content = self.content_at_path(path)
        if not content:
            raise KeyError(f'There is no content at path "{path}"')
        return self.copy(content=content, url=self / path + '/')

    def __iter__(self) -> Iterator[IncludedContent]:
        """Iterate `Content` objects in this collection."""
        return iter(self.content)

    def content_at_path(self, target: str) -> Collection[IncludedContent]:
        target_parts = Path(target).parts
        new_path = lambda source: '/'.join(source[len(target_parts):])
        result = []
        for ic in self.content:
            source_parts = Path(ic.path).parts
            if all(actual == expected for actual, expected in zip(source_parts, target_parts)):
                result.append(replace(ic, path=new_path(source_parts)))
        return result

    def __contains__(self, path: str) -> bool:
        return path in map(lambda c: c.path, self.content)


def file_or_dir(path: Path):
    return FileCopy(path) if path.is_file() else DirectoryCopy(path)


@dataclass(frozen=True)
class IncludedContent:
    path: str
    content: Content
    cwd: str


@dataclass(frozen=True)
class Author:
    name: Optional[str] = None
    email: Optional[str] = None
