from __future__ import annotations

from abc import ABC
from datetime import datetime
from pathlib import Path
from typing import Mapping, Dict, TYPE_CHECKING, Collection, Iterator, Any, Tuple
from urllib.parse import urljoin

if TYPE_CHECKING:
    from lightweight import Content

# Type aliases for clear type definitions
Url = str
LanguageCode = str
Email = str


class ContentCollection:
    """A collection of Content that can be queried and iterated."""

    def __init__(self, content: Mapping[Path, Content]):
        self.content = dict(content)

    def __getitem__(self, path_part: str) -> ContentAtPath:
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

        content = self.content_at_path(Path(path_part))
        if not content:
            raise KeyError(f'There is no content at path "{path_part}"')
        return ContentAtPath(self, Path(path_part), content)

    def __iter__(self) -> Iterator[Content]:
        """Iterate `Content` objects in this collection."""
        return iter(self.content.values())

    def content_at_path(self, target: Path):
        index = len(target.parts)
        return {
            path: content
            for path, content in self.content.items()
            if len(path.parts) > index and all(actual == expected for actual, expected in zip(path.parts, target.parts))
        }

    def __contains__(self, content: Content) -> bool:
        return content in self.content.values()


class EntryCollection(ABC):
    """A specification of an Entry Collection interface. Entry collection has properties like url, title, author,
     datetime of update which allow it to be used by other components, e.g. feeds.
    """

    take_after_fields = frozenset({
        'url', 'icon_url', 'title', 'description', 'author_name', 'author_email', 'language', 'copyright', 'updated'
    })
    url: Url
    icon_url: Url
    title: str
    description: str
    author_name: str
    author_email: Email
    language: LanguageCode
    copyright: str  # Full notice.
    updated: datetime

    def take_after(self, source: Any = None, **custom: Any) -> None:
        """A simple way to copy Entry Collection properties from one object to another."""

        if source:
            for field, value in self.field_value(source, self.take_after_fields - custom.keys()):
                setattr(self, field, value)
        for field, value in custom.items():
            setattr(self, field, value)

    @classmethod
    def field_value(cls, collection: EntryCollection, fields: Collection[str]) -> Iterator[Tuple[str, Any]]:
        return (
            (field, getattr(collection, field))
            for field in fields
            if hasattr(collection, field)
        )


class ContentAtPath(EntryCollection, ContentCollection):
    """Content Collection retrieved by accessing other content collection by path:

            :Example:
            >>> site = Site(url='http://example.org', ...) # site is a collection of content

            >>> site.include('index.html', <index>)
            >>> site.include('posts/dev/1', <post-1>)
            >>> site.include('posts/dev/2', <post-2>)
            >>> site.include('posts/other/3', <post-3>)
            >>> site.include('static', <static>)

            >>> posts = site['posts']
            >>> dev_posts = posts['dev']
            >>> assert dev_posts.url is 'http://example.org/posts/dev'
            >>> assert <post-1> in posts
            >>> assert <post-2> in posts
            >>> assert <post-3> not in posts
            >>> assert <static> not in posts
    """

    def __init__(self, source: ContentCollection, path: Path, content: Dict[Path, Content]):
        super().__init__(content)
        self.relative_path = path

        root_url = getattr(source, 'url', '')
        url = urljoin(root_url, str(path))
        source_title = getattr(source, 'title', None)
        description = f'{source_title} | {self.relative_path}' if source_title else url
        self.take_after(source, url=url, description=description)

    def __getitem__(self, path_part: str):
        path = self.relative_path / path_part
        return ContentAtPath(self, path, self.content_at_path(path))
