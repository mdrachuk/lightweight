from __future__ import annotations

import asyncio
import os
from abc import abstractmethod, ABC
from asyncio import gather
from collections import defaultdict
from dataclasses import dataclass, replace
from datetime import datetime
from itertools import chain
from os import getcwd
from os.path import abspath
from pathlib import Path
from shutil import rmtree
from typing import overload, Union, Optional, Collection, List, Set, Dict
from urllib.parse import urlparse, urljoin

from lightweight.content.content import Content
from lightweight.content.copies import copy
from lightweight.empty import Empty, empty
from lightweight.errors import AbsolutePathIncluded, IncludedDuplicate
from lightweight.files import paths, directory
from lightweight.generation import GenContext, GenTask, schedule


class Site:
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
    content: Includes
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
            content: Includes = None,
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
        self.content = Includes() if not content else content
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
            content: Union[Includes, Empty] = empty,
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
    def include(self, location: str, content: Site):
        """Include the content at the provided location."""

    @overload
    def include(self, location: str, content: str):
        """Copy files from content to location."""

    def include(self, location: str, content: Union[Content, Site, str, None] = None):
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
                raise FileNotFoundError(f'There were no files at paths: {location}')
            [self._include_content(path, content_, cwd) for path, content_ in contents.items()]
        elif isinstance(content, Content):
            self._include_content(location, content, cwd)
        elif isinstance(content, Site):
            self._include_site(location, content, cwd)
        elif isinstance(content, str):
            source = Path(content)
            if not source.exists():
                raise FileNotFoundError(f'File does not exist: {content}')
            self._include_content(location, copy(source), cwd)
        else:
            raise ValueError('Content, str, or None types are accepted as include parameter')

    def _include_content(self, location: str, content: Content, cwd: str):
        self._include(
            IncludedContent(
                location=location,
                content=content,
                cwd=cwd
            )
        )

    def _include_site(self, location: str, site: Site, cwd: str):
        self._include(
            IncludedSite(
                location=location,
                site=site,
                cwd=cwd
            )
        )

    def _include(self, c: Included):
        if c.location in self.content:
            raise IncludedDuplicate(at=c.location)
        self.content.add(c)

    def generate(self, out: Union[str, Path] = 'out'):
        """Generate the site in directory provided as out.

        If the out directory does not exist — it will be created along with its whole hierarchy.

        If the out directory already exists – it will be deleted with all of it contents.
        """
        out = Path(abspath(out))
        if out.exists():
            rmtree(out)
        out.mkdir(parents=True, exist_ok=True)
        self._generate(out)

    def _generate(self, out: Path):
        ctx = GenContext(out=out, site=self)
        tasks = defaultdict(list)  # type: Dict[str, List[GenTask]]
        all_tasks = list()  # type: List[GenTask]
        for ic in self.content:
            _tasks = ic.make_tasks(ctx)
            for task in _tasks:
                tasks[task.cwd].append(task)
            all_tasks.extend(_tasks)
        ctx.tasks = tuple(all_tasks)  # injecting tasks, for other content to have access to site structure

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        for cwd, _tasks in tasks.items():
            with directory(cwd):
                writes = [schedule(task.content.write, task.path, ctx) for task in _tasks]
                loop.run_until_complete(gather(*writes, loop=loop))
        loop.close()

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
        content = self.content.at_path(Path(location))
        if not content:
            raise KeyError(f'There is no content at path "{location}"')
        return self.copy(content=content, url=self / location + '/')


def clip_path_parts(number: int, path: Path) -> str:
    return os.path.join(*path.parts[number:])


class Includes:
    ics: List[Included]
    by_cwd: Dict[str, List[Included]]
    by_location: Dict[str, Included]

    def __init__(self):
        self.ics = []
        self.by_cwd = defaultdict(list)
        self.by_location = {}

    def add(self, ic: Included):
        self.ics.append(ic)
        self.by_cwd[ic.cwd].append(ic)
        self.by_location[ic.location] = ic

    def __contains__(self, location: str) -> bool:
        return location in self.by_location

    def __iter__(self):
        return iter(self.ics)

    def __getitem__(self, location: str):
        return self.by_location[location]

    def at_path(self, target: Path) -> Includes:
        target = Path(target)
        cc = Includes()
        for ic in self.ics:
            if all(actual == expected for actual, expected in zip(ic.path.parts, target.parts)):
                new_loc = clip_path_parts(len(target.parts), ic.path)
                new_ic = replace(ic, location=new_loc)
                cc.add(new_ic)
        return cc


class Included(ABC):
    location: str
    cwd: str

    @property
    def path(self):
        return Path(self.location)

    @abstractmethod
    def make_tasks(self, ctx: GenContext) -> List[GenTask]:
        """"""


@dataclass(frozen=True)
class IncludedContent(Included):
    """The [content][Content] included by a [Site].

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

    def make_tasks(self, ctx: GenContext) -> List[GenTask]:
        return [GenTask(ctx.path(self.location), self.content, self.cwd)]


@dataclass(frozen=True)
class IncludedSite(Included):
    """Another site included by a [Site].

    Contains the relative location and `cwd` (current working directory) of the content.

    Location is a string with an output path relative to generation out directory.
    It does not include a leading forward slash.

    `cwd` is important for properly generating subsites.
    """
    location: str
    site: Site
    cwd: str

    @property
    def path(self):
        return Path(self.location)

    def make_tasks(self, ctx: GenContext) -> List[GenTask]:
        list_of_lists = [ic.make_tasks(ctx) for ic in self.site.content.ics]
        tasks = list(chain.from_iterable(list_of_lists))
        return [replace(task, path=ctx.path(self.path / task.path.relative_path)) for task in tasks]


@dataclass(frozen=True)
class Author:
    """An author. Mostly used by RSS/Atom."""
    name: Optional[str] = None
    email: Optional[str] = None
