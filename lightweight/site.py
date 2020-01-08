from __future__ import annotations

import os
from dataclasses import dataclass, replace
from datetime import datetime
from os import getcwd
from pathlib import Path
from shutil import rmtree
from typing import overload, Union, Optional, Collection, Iterator, List, Set
from urllib.parse import urlparse, urljoin

from lightweight.content.content import Content
from lightweight.content.copies import copy
from lightweight.empty import Empty, empty
from lightweight.errors import AbsolutePathIncluded, IncludedDuplicate
from lightweight.files import paths, directory
from lightweight.generation import GenContext, GenPath, GenTask


class Site(Content):
    """A static site for generation, which is basically a collection of [Content].

    Site is one of the few mutable Lightweight components. It is available to content during [write][Content.write],
    as a property of the [provided ctx][GenContext].

    The only required parameter is the URL of the site. Other parameters may be useful for different content types.

    @example
    The following code output to the `out` directory the following content:
    - two rendered Jinja 2 HTML templates;
    - CSS rendered from SCSS;
    - copies of `img` and `js` directories.

    ```
    site = Site('https://example.org/')

    site.include('index.html', jinja('index.html'))
    site.include('about.html', jinja('about.html'))
    site.include('css/style.css', sass('styles/main.scss'))
    site.include('img')
    site.include('js')

    site.generate(out='out')
    ```
    """
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
        if not url.endswith('/'):
            raise ValueError(f'Site URL ({url}) must end with a forward slash (/).')
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
        """Creates a new Site which copies the attributes of the current one.

        Some property values can be overriden, by providing them to this method.
        """
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
    def include(self, location: str):
        """Include a file, a directory, or multiple files with a glob pattern."""

    @overload
    def include(self, location: str, content: Content):
        """Include the content at the provided location."""

    @overload
    def include(self, location: str, content: str):
        """Copy files from content to location."""

    def include(self, location: str, content: Union[Content, str, None] = None):
        """Included the content at the location.

        Note the content write is executed only upon calling [`Site.generate()`][Site.generate].

        The location cannot be absolute. It cannot start with a forward slash.

        During the include the `cwd` (current working directory) is recorded.
        The [content’s write][Content.write] will be executed from this directory.

        Check overloads for alternative signatures."""
        cwd = getcwd()
        if location.startswith('/'):
            raise AbsolutePathIncluded()
        if content is None:
            contents = {str(path): copy(path) for path in paths(location)}
            if not len(contents):
                raise FileNotFoundError()
            [self._include(path, content_, cwd) for path, content_ in contents.items()]
        elif isinstance(content, Content):
            self._include(location, content, cwd)
        elif isinstance(content, str):
            source = Path(content)
            if not source.exists():
                raise FileNotFoundError()
            self._include(location, copy(source), cwd)
        else:
            raise Exception(ValueError('Content, str, or None types are accepted as include parameter'))

    def _include(self, location: str, content: Content, cwd: str):
        if location in self:
            raise IncludedDuplicate()
        self.content.append(
            IncludedContent(
                location=location,
                content=content,
                cwd=cwd
            )
        )

    def generate(self, out: Union[str, Path] = 'out'):
        """Generate the site in directory provided as out.

        If the out directory does not exist — it will be created along with its whole hierarchy.

        If the out directory already exists – it will be deleted with all of it contents.
        """
        out = Path(out)
        if out.exists():
            rmtree(out)
        out.mkdir(parents=True, exist_ok=True)
        self._generate(out)

    def write(self, path: GenPath, ctx: GenContext):
        """Write the current site at path.

        Executed when this site is part of the other site."""
        self._generate((ctx.out / path.relative_path).absolute())

    def _generate(self, out: Path):
        ctx = GenContext(out=out, site=self)
        tasks = [GenTask(ctx.path(c.path), c.content, c.cwd) for c in ctx.site.content]
        ctx.tasks = tuple(tasks)  # injecting tasks, for other content to have access to site structure
        for task in tasks:
            with directory(task.cwd):
                task.content.write(task.path, ctx)

    def __repr__(self):
        return f'<{type(self).__name__} title={self.title} url={self.url} at 0x{id(self):02x}>'

    def __truediv__(self, location: str):
        """Create a URL for the location at site.

        @example
        site = Site('https://example.org/')

        url = site / 'resource/images/photo-1.jpeg'
        print(url) # https://example.org/resource/images/photo-1.jpeg
        """

        return urljoin(self.url, location)

    def __getitem__(self, location: str) -> Site:
        """Get a site with a subset of the this sites content, which is included at the provided path.

        @example
        ```python
        site = Site(url='https://example.org/', ...) # site is a collection of content

        site.include('index.html', <index>)
        site.include('posts/1', <post-1>)
        site.include('posts/2', <post-2>)
        site.include('posts/3', <post-3>)
        site.include('static', <static>)

        posts = site['posts']
        assert posts.url is 'https://example.org/posts'
        assert <post-1> in posts
        assert <post-2> in posts
        assert <post-3> in posts
        assert <static> not in posts
        ```
        """
        content = self.content_at_path(Path(location))
        if not content:
            raise KeyError(f'There is no content at path "{location}"')
        return self.copy(content=content, url=self / location + '/')

    def __iter__(self) -> Iterator[IncludedContent]:
        """Iterate over the site’s included content."""
        return iter(self.content)

    def content_at_path(self, target: Path) -> Collection[IncludedContent]:
        target = Path(target)
        return [
            replace(ic, location=clip_path_parts(len(target.parts), ic.path))
            for ic in self.content
            if all(actual == expected for actual, expected in zip(ic.path.parts, target.parts))
        ]

    def __contains__(self, location: str) -> bool:
        return location in map(lambda c: c.location, self.content)


def clip_path_parts(number: int, path: Path) -> str:
    return os.path.join(*path.parts[number:])


@dataclass(frozen=True)
class IncludedContent:
    """The [content][Content] included by [Site].

    Contains the site’s location and `cwd` (current working directory) of the content.

    Location is a string with an output path relative to generation out directory.
    It does not include a leading forward slash.

    `cwd` is important for properly generating subsites.
    """
    location: str
    content: Content
    cwd: str

    @property
    def path(self):
        return Path(self.location)


@dataclass(frozen=True)
class Author:
    """An author. Mostly used by RSS/Atom."""
    name: Optional[str] = None
    email: Optional[str] = None
