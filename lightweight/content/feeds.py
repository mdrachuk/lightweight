from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, TypeVar, Any, Optional, Type, List, Mapping, Union
from urllib.parse import urljoin

from feedgen.entry import FeedEntry  # type: ignore
from feedgen.feed import FeedGenerator  # type: ignore

from lightweight.content import Content

if TYPE_CHECKING:
    from lightweight import ContentCollection, RenderPath, Site, Rendering

# Type aliases for clear type definitions
Url = str
LanguageCode = str
Email = str


@dataclass(frozen=True)
class RssFeed(Content):
    """An immutable RSS feed content that can be saved to a file."""
    url: Url
    icon_url: Optional[Url]
    title: str
    description: str
    updated: Optional[str]
    author: Mapping[str, Optional[str]]
    language: Optional[LanguageCode]
    copyright: Optional[str]

    entries: List[Entry]

    def render(self, ctx: Rendering):
        gen = FeedGenerator()

        gen.id(self.url)
        gen.link(href=self.url, rel='alternate')
        gen.icon(self.icon_url)
        gen.title(self.title)
        gen.description(self.description)

        if self.updated:
            gen.updated(self.updated)

        gen.author(self.author)

        gen.language(self.language)
        gen.copyright(self.copyright)

        for entry in self.entries:
            feed_entry = gen.add_entry()
            entry.fill(feed_entry, ctx)

        return gen.rss_str(pretty=True)

    def write(self, path: RenderPath):
        target = self.render(path.ctx)
        path.create(target)


@dataclass(frozen=True)
class AtomFeed(Content):
    """An immutable Atom feed content that can be saved to a file."""
    url: str
    icon_url: Optional[str]
    title: str
    description: str
    updated: Optional[datetime]
    author: Mapping[str, Optional[str]]
    language: Optional[str]
    copyright: Optional[str]

    entries: List[Entry]

    def render(self, ctx: Rendering):
        gen = FeedGenerator()

        gen.id(self.url)
        gen.link(href=self.url, rel='alternate')
        gen.icon(self.icon_url)
        gen.title(self.title)
        gen.description(self.description)

        if self.updated:
            gen.updated(self.updated)

        gen.author(self.author)

        gen.language(self.language)
        gen.copyright(self.copyright)

        for entry in self.entries:
            feed_entry = gen.add_entry()
            entry.fill(feed_entry, ctx)

        return gen.atom_str(pretty=True)

    def write(self, path: RenderPath):
        target = self.render(path.ctx)
        path.create(target)


@dataclass(frozen=True)
class Entry:
    url: str
    title: str
    author: Mapping[str, Optional[str]]
    created: datetime
    updated: datetime
    summary: str

    def fill(self, feed_entry: FeedEntry, ctx: Rendering):
        """Fill the provided FeedEntry with content."""
        feed_entry.id(self.url)
        feed_entry.link(href=self.url, rel='alternate')

        feed_entry.title(self.title)

        feed_entry.summary(self.summary)
        # TODO:mdrachuk:2019-09-02: support tags (categories)
        # TODO:mdrachuk:2019-09-02: support rich media (videos, audio)

        feed_entry.author(self.author)
        # TODO:mdrachuk:2019-09-02: support contributors

        feed_entry.published(self.created)
        feed_entry.updated(self.updated)


def atom(source: ContentCollection) -> AtomFeed:
    return new_feed(AtomFeed, source)


def rss(source: ContentCollection) -> RssFeed:
    return new_feed(RssFeed, source)


F = TypeVar('F', RssFeed, AtomFeed)


def new_feed(feed: Type[F], source: ContentCollection) -> F:
    """Create RSS and Atom feeds."""

    url = required(source, 'url')
    icon_url = get(source, 'icon_url', default=None)
    title = required(source, 'title')
    description = required(source, 'description')

    updated = get(source, 'updated', default=None)
    author = {
        'name': get(source, 'author_name', default=None),
        'email': get(source, 'author_email', default=None),
    }
    language = get(source, 'language', default=None)
    copyright = get(source, 'copyright', default=None)

    entries = [new_entry(path, entry_content, author, url) for path, entry_content in source.content.items()]

    return feed(
        url=url,
        icon_url=icon_url,
        title=title,
        description=description,
        updated=updated,
        author=author,
        language=language,
        copyright=copyright,
        entries=entries,
    )


def new_entry(location: str, content: Content, author: Any, root_url: Url, ):
    """Fill the provided FeedEntry with content."""
    url = get(content, 'url', default=urljoin(root_url, location))
    title = get(content, 'title', default=location)
    summary = get(content, 'summary', default='')
    created = get(content, 'created', default=datetime.now(tz=timezone.utc))
    updated = get(content, 'updated', default=created)
    return Entry(
        url=url,
        title=title,
        summary=summary,
        author=author,
        created=created,
        updated=updated,
    )


T = TypeVar('T')


def required(obj, field: str) -> Any:
    """Get a field from object, raising a Value error if its not present, None, or empty."""
    value = getattr(obj, field, None)
    if not value and value is not False and value != 0:
        raise ValueError(f'"{field}" is required to construct a feed. It cannot be missing, None, or empty.')
    return value


def get(obj, field: str, *, default: T) -> Union[T, Any]:
    """Get a field from object, with a default value in case its not present, None, or empty."""
    value = getattr(obj, field, None)
    if not value and value is not False and value != 0:
        return default
    return value
