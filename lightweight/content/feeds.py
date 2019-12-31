from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, Mapping, Tuple, Generic, TypeVar, List
from urllib.parse import urljoin

from feedgen import feed as fgf # type: ignore
from feedgen import entry as fge # type: ignore

from lightweight.content import Content
from .markdown import MarkdownPage

if TYPE_CHECKING:
    from lightweight import Site, RenderPath


@dataclass(frozen=True)
class RssFeed(Content):
    """An immutable RSS feed content that can be saved to a file."""
    url: str
    icon_url: Optional[str]
    title: str
    description: str
    updated: Optional[str]
    author: Mapping[str, Optional[str]]
    language: Optional[str]
    copyright: Optional[str]

    entries: Tuple[RssEntry, ...]

    def render(self):
        gen = fgf.FeedGenerator()

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
            entry.fill(feed_entry)

        return gen.rss_str(pretty=True)

    def write(self, path: RenderPath):
        target = self.render()
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

    entries: Tuple[AtomEntry, ...]

    def render(self):
        gen = fgf.FeedGenerator()

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
            entry.fill(feed_entry)

        return gen.atom_str(pretty=True)

    def write(self, path: RenderPath):
        target = self.render()
        path.create(target)


@dataclass(frozen=True)
class RssEntry:
    url: str
    title: str
    author: Mapping[str, Optional[str]]
    created: datetime
    updated: datetime
    summary: str
    path: str

    def fill(self, feed_entry: fge.FeedEntry):
        """Fill the provided FeedEntry with content."""
        feed_entry.id(self.path)
        feed_entry.link(href=self.url, rel='alternate')

        feed_entry.title(self.title)

        feed_entry.summary(self.summary)
        # TODO:mdrachuk:2019-09-02: support tags (categories)
        # TODO:mdrachuk:2019-09-02: support rich media (videos, audio)

        feed_entry.author(self.author)
        # TODO:mdrachuk:2019-09-02: support contributors

        feed_entry.published(self.created)
        feed_entry.updated(self.updated)


@dataclass(frozen=True)
class AtomEntry:
    url: str
    title: str
    author: Mapping[str, Optional[str]]
    created: datetime
    updated: datetime
    summary: str
    path: str

    def fill(self, feed_entry: fge.FeedEntry):
        """Fill the provided FeedEntry with content."""
        feed_entry.id(self.path)
        feed_entry.link(href=self.url, rel='alternate')

        feed_entry.title(self.title)

        feed_entry.summary(self.summary)
        # TODO:mdrachuk:2019-09-02: support tags (categories)
        # TODO:mdrachuk:2019-09-02: support rich media (videos, audio)

        feed_entry.author(self.author)
        # TODO:mdrachuk:2019-09-02: support contributors

        feed_entry.published(self.created)
        feed_entry.updated(self.updated)


T = TypeVar('T')


class EntryFactory(ABC, Generic[T]):

    @abstractmethod
    def rss(self, location: str, content: T, site: Site) -> RssEntry:
        """"""

    @abstractmethod
    def atom(self, location: str, content: T, site: Site) -> AtomEntry:
        """"""

    @abstractmethod
    def accepts(self, path: str, content: Content):
        """"""


class MarkdownEntries(EntryFactory):

    def accepts(self, path: str, content: Content):
        return isinstance(content, MarkdownPage)

    def atom(self, location: str, content: MarkdownPage, site: Site) -> AtomEntry:
        url = urljoin(site.url, location)
        title = content.title or location
        summary = content.summary or ''
        created = content.created or datetime.now(tz=timezone.utc)
        updated = content.updated or created
        return AtomEntry(
            url=url,
            title=title,
            summary=summary,
            author={'name': site.author_name, 'email': site.author_email},
            created=created,
            updated=updated,
            path=location,
        )

    def rss(self, location: str, content: MarkdownPage, site: Site) -> RssEntry:
        url = urljoin(site.url, location)
        title = content.title or location
        summary = content.summary or ''
        created = content.created or datetime.now(tz=timezone.utc)
        updated = content.updated or created
        return RssEntry(
            url=url,
            title=title,
            summary=summary,
            author={'name': site.author_name, 'email': site.author_email},
            created=created,
            updated=updated,
            path=location,
        )


class FeedGenerator:
    _factories: List[EntryFactory]

    def __init__(self):
        self._factories = []

    def _factory(self, path, content):
        for factory in self._factories:
            if factory.accepts(path, content):
                return factory
        else:
            raise ValueError()  # TODO:mdrachuk:31.12.2019: set error message

    def add_factory(self, factory: EntryFactory):
        self._factories.insert(0, factory)


class RssGenerator(FeedGenerator):
    def __call__(self, source: Site):
        """Create RSS and Atom feeds."""

        author = {
            'name': source.author_name,
            'email': source.author_email,
        }
        entries = [
            self._factory(ic.path, ic.content)
                .rss(ic.path, ic.content, source)
            for ic in source.content
        ]

        return RssFeed(
            url=source.url,
            icon_url=source.icon_url,
            title=source.title,
            description=source.description,
            updated=source.updated,
            author=author,
            language=source.language,
            copyright=source.copyright,
            entries=tuple(entries),
        )


class AtomGenerator(FeedGenerator):
    def __call__(self, source: Site):
        """Create RSS and Atom feeds."""
        author = {
            'name': source.author_name,
            'email': source.author_email,
        }
        entries = [
            self._factory(ic.path, ic.content)
                .atom(ic.path, ic.content, source)
            for ic in source.content
        ]

        return AtomFeed(
            url=source.url,
            icon_url=source.icon_url,
            title=source.title,
            description=source.description,
            updated=source.updated,
            author=author,
            language=source.language,
            copyright=source.copyright,
            entries=tuple(entries),
        )


atom = AtomGenerator()
atom.add_factory(MarkdownEntries())

rss = RssGenerator()
rss.add_factory(MarkdownEntries())
