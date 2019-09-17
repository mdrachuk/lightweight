from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar, Any, Optional

from feedgen.entry import FeedEntry
from feedgen.feed import FeedGenerator

from lightweight.content import Content
from lightweight.content.content import Entry

if TYPE_CHECKING:
    from lightweight import ContentCollection, SitePath

# Type aliases for clear type definitions
Url = str
LanguageCode = str
Email = str


class FeedString(Content, bytes):

    def render(self, path: SitePath):
        path.create(self)

    def __repr__(self):
        return f'<Feed {truncate(self)}>'


class RssFeed(FeedString):

    def __repr__(self):
        return f'<RssFeed {truncate(self)}>'


class AtomFeed(FeedString):

    def __repr__(self):
        return f'<AtomFeed {truncate(self)}>'


@dataclass(frozen=True)
class Feed:
    rss: RssFeed
    atom: AtomFeed


def feed(content: ContentCollection, include_content=True) -> Feed:
    """Create a content feed"""
    gen = FeedGenerator()

    # TODO:mdrachuk:9/10/19: better error messages
    # TODO:mdrachuk:9/10/19: document behaviour (take after pattern)
    gen.id(required(content, 'url'))
    gen.link(href=required(content, 'url'), rel='alternate')
    gen.icon(get(content, 'icon_url', default=None))
    gen.title(required(content, 'title'))
    gen.description(required(content, 'description'))

    updated = get(content, 'updated', default=None)
    if updated is not None:
        gen.updated(updated)

    author = {
        'name': get(content, 'author_name', default=None),
        'email': get(content, 'author_email', default=None),
    }
    gen.author(author)

    gen.language(get(content, 'language', default=None))
    gen.copyright(get(content, 'copyright', default=None))

    for path, entry in content.content.items():
        feed_entry = gen.add_entry()
        fill_entry(path, entry, feed_entry, author, include_content=include_content)

    return Feed(
        RssFeed(gen.rss_str(pretty=True)),
        AtomFeed(gen.atom_str(pretty=True))
    )


def fill_entry(path: Path, entry: Entry, feed_entry: FeedEntry, author: Any, *, include_content: bool):
    link = get(entry, 'url', default=str(path))  # TODO:mdrachuk:9/11/19: make absolute
    feed_entry.id(link)
    feed_entry.link(href=link, rel='alternate')

    feed_entry.title(get(entry, 'title', default=str(path)))

    if include_content:
        # TODO:mdrachuk:2019-09-02: support tags (categories)
        # TODO:mdrachuk:2019-09-02: support summary/content
        # TODO:mdrachuk:2019-09-02: rich media (videos, audio)
        feed_entry.content(entry.content)

    feed_entry.author(getattr(entry, 'author', author))
    # TODO:mdrachuk:2019-09-02: support contributors

    created = get(entry, 'created', default=datetime.now(tz=timezone.utc))
    feed_entry.published(created)
    feed_entry.updated(get(entry, 'updated', default=created))


T = TypeVar('T')


def required(obj, field: str) -> Any:
    value = getattr(obj, field, None)
    if value is None:
        raise ValueError(f'"{field}" can’t be missing or None.')
    return value


def get(obj, field: str, *, default: Optional[T]) -> Optional[T]:
    value = getattr(obj, field, None)
    return value if value is not None else default


def truncate(string: str, size=16) -> str:
    return f'{string[:size]}..' if len(string) > size else string
