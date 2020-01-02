from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, Tuple, Generic, TypeVar, List
from urllib.parse import urljoin

from feedgen import entry as fge  # type: ignore
from feedgen import feed as fgf  # type: ignore

from lightweight.content import Content
from .markdown import MarkdownPage

if TYPE_CHECKING:
    from lightweight import Site, RenderPath, Author


@dataclass(frozen=True)
class RssFeed(Content):
    """An immutable RSS feed content that can be saved to a file."""
    url: str
    title: str
    description: str
    updated: Optional[datetime]
    authors: Tuple[Author, ...]
    language: Optional[str]
    copyright: Optional[str]

    entries: Tuple[RssEntry, ...]

    def render(self):
        generator = self._generator()
        self._add_entries(generator)
        return generator.rss_str(pretty=True)

    def _generator(self) -> fgf.FeedGenerator:
        gen = fgf.FeedGenerator()

        gen.id(self.url)
        gen.link(href=self.url, rel='alternate')
        gen.title(self.title)
        gen.description(self.description)

        if self.updated:
            gen.updated(self.updated)

        gen.author(list(map(asdict, self.authors)))

        gen.language(self.language)
        gen.copyright(self.copyright)

        return gen

    def _add_entries(self, gen: fgf.FeedGenerator):
        for entry in self.entries:
            feed_entry = gen.add_entry()
            entry.fill(feed_entry)

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
    authors: Tuple[Author, ...]
    language: Optional[str]
    copyright: Optional[str]

    entries: Tuple[AtomEntry, ...]

    def render(self):
        generator = self._generator()
        self._add_entries(generator)
        return generator.atom_str(pretty=True)

    def _generator(self):
        gen = fgf.FeedGenerator()

        gen.id(self.url)
        gen.link(href=self.url, rel='alternate')
        gen.icon(self.icon_url)
        gen.title(self.title)
        gen.description(self.description)

        if self.updated:
            gen.updated(self.updated)

        gen.author(list(map(asdict, self.authors)))

        gen.language(self.language)  # only sets xml:lang property of the feed node
        gen.rights(self.copyright)

        return gen

    def _add_entries(self, gen: fgf.FeedGenerator):
        for entry in self.entries:
            feed_entry = gen.add_entry()
            entry.fill(feed_entry)

    def write(self, path: RenderPath):
        target = self.render()
        path.create(target)


@dataclass(frozen=True)
class RssEntry:
    url: str
    title: str
    authors: Tuple[Author, ...]
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

        feed_entry.author(list(map(asdict, self.authors)))
        # TODO:mdrachuk:2019-09-02: support contributors

        feed_entry.published(self.created)
        feed_entry.updated(self.updated)


@dataclass(frozen=True)
class AtomEntry:
    url: str
    title: str
    authors: Tuple[Author, ...]
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

        feed_entry.author(list(map(asdict, self.authors)))
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
    def accepts(self, path: str, content: Content) -> bool:
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
            authors=tuple(site.authors),
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
            authors=tuple(site.authors),
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
        """Create an RSS feed."""
        authors = tuple(source.authors)
        entries = [
            self._factory(ic.path, ic.content)
                .rss(ic.path, ic.content, source)
            for ic in source.content
        ]

        if not source.title or not source.description or not source.updated:
            raise ValueError()

        return RssFeed(
            url=source.url,
            title=source.title,
            description=source.description,
            updated=source.updated,
            authors=authors,
            language=source.language,
            copyright=source.copyright,
            entries=tuple(entries),
        )


class AtomGenerator(FeedGenerator):
    def __call__(self, source: Site):
        """Create an Atom feed."""
        entries = [
            self._factory(ic.path, ic.content)
                .atom(ic.path, ic.content, source)
            for ic in source.content
        ]
        if not source.title or not source.description:
            raise ValueError()

        return AtomFeed(
            url=source.url,
            icon_url=source.icon_url,
            title=source.title,
            description=source.description,
            updated=source.updated,
            authors=tuple(source.authors),
            language=source.language,
            copyright=source.copyright,
            entries=tuple(entries),
        )


_md_entry_factory = MarkdownEntries()

atom = AtomGenerator()
atom.add_factory(_md_entry_factory)

rss = RssGenerator()
rss.add_factory(_md_entry_factory)
