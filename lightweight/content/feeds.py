from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar, Any, Optional, Iterator, Tuple
from urllib.parse import urljoin

from feedgen.entry import FeedEntry  # type: ignore
from feedgen.feed import FeedGenerator  # type: ignore

from lightweight.content import Content
from lightweight.content.content import ByteContent

if TYPE_CHECKING:
    from lightweight import ContentCollection

# Type aliases for clear type definitions
Url = str
LanguageCode = str
Email = str


class RssFeed(ByteContent):
    """An immutable RSS feed content that can be saved to a file."""


class AtomFeed(ByteContent):
    """An immutable Atom feed content that can be saved to a file."""


@dataclass(frozen=True)
class Feeds:
    rss: RssFeed
    atom: AtomFeed

    def __iter__(self) -> Iterator[Tuple[str, ByteContent]]:
        return iter([
            ('rss', self.rss),
            ('atom', self.atom),
        ])


def feeds(content: ContentCollection, include_content=True) -> Feeds:
    """Create RSS and Atom feeds."""
    gen = FeedGenerator()

    url = required(content, 'url')
    gen.id(url)
    gen.link(href=url, rel='alternate')
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
        fill_entry(path, entry, feed_entry, author, url, include_content=include_content)

    return Feeds(
        RssFeed(gen.rss_str(pretty=True)),
        AtomFeed(gen.atom_str(pretty=True))
    )


def fill_entry(
        path: Path,
        content: Content,
        feed_entry: FeedEntry,
        author: Any,
        root_url: Url,
        *,
        include_content: bool
):
    """Fill the provided FeedEntry with content."""
    url = get(content, 'url', default=urljoin(root_url, str(path)))
    feed_entry.id(url)
    feed_entry.link(href=url, rel='alternate')

    feed_entry.title(get(content, 'title', default=str(path)))

    if include_content:
        # TODO:mdrachuk:2019-09-02: support tags (categories)
        # TODO:mdrachuk:2019-09-02: support summary/content
        # TODO:mdrachuk:2019-09-02: rich media (videos, audio)
        feed_entry.content(required(content, 'content'))

    feed_entry.author(getattr(content, 'author', author))
    # TODO:mdrachuk:2019-09-02: support contributors

    created = get(content, 'created', default=datetime.now(tz=timezone.utc))
    feed_entry.published(created)
    feed_entry.updated(get(content, 'updated', default=created))


T = TypeVar('T')


def required(obj, field: str) -> Any:
    """Get a field from object, raising a Value error if its not present, None, or empty."""
    value = getattr(obj, field, None)
    if not value and value is not False and value != 0:
        raise ValueError(f'"{field}" is required to construct a feed. It cannot be missing, None, or empty.')
    return value


def get(obj, field: str, *, default: Optional[T]) -> Optional[T]:
    """Get a field from object, with a default value in case its not present, None, or empty."""
    value = getattr(obj, field, None)
    if not value and value is not False and value != 0:
        return default
    return value
