from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, Tuple, Generic, TypeVar, List

from feedgen import entry as fge  # type: ignore
from feedgen import feed as fgf  # type: ignore

from lightweight.content import Content
from .markdown import MarkdownPage

if TYPE_CHECKING:
    from lightweight import Site, GenPath, Author, GenContext


@dataclass(frozen=True)
class RssFeed(Content):
    """An immutable RSS feed content that can be saved to a file."""
    url: str
    image_url: Optional[str]
    title: str
    description: str
    updated: Optional[datetime]
    authors: Tuple[Author, ...]
    language: Optional[str]
    copyright: Optional[str]

    entries: Tuple[RssEntry, ...]

    def compile(self):
        return self._as_fg().rss_str(pretty=True)

    def _as_fg(self) -> fgf.FeedGenerator:
        gen = fgf.FeedGenerator()

        gen.id(self.url)
        gen.link(href=self.url, rel='alternate')
        gen.title(self.title)
        gen.description(self.description)
        gen.image(self.image_url)

        if self.updated:
            gen.updated(self.updated)

        gen.author(list(map(asdict, self.authors)))

        gen.language(self.language)
        gen.copyright(self.copyright)

        [gen.add_entry(entry._as_fg()) for entry in self.entries]

        return gen

    def write(self, path: GenPath, ctx: GenContext):
        target = self.compile()
        path.create(target)


@dataclass(frozen=True)
class AtomFeed(Content):
    """An immutable Atom feed content that can be saved to a file."""
    url: str
    icon_url: Optional[str]
    logo_url: Optional[str]
    title: str
    description: str
    updated: Optional[datetime]
    authors: Tuple[Author, ...]
    language: Optional[str]
    copyright: Optional[str]

    entries: Tuple[AtomEntry, ...]

    def compile(self):
        return self._as_fg().atom_str(pretty=True)

    def _as_fg(self):
        gen = fgf.FeedGenerator()

        gen.id(self.url)
        gen.link(href=self.url, rel='alternate')
        gen.icon(self.icon_url)
        gen.logo(self.logo_url)
        gen.title(self.title)
        gen.description(self.description)

        if self.updated:
            gen.updated(self.updated)

        gen.author(list(map(asdict, self.authors)))

        gen.language(self.language)  # only sets xml:lang property of the feed node
        gen.rights(self.copyright)

        [gen.add_entry(entry._as_fg()) for entry in self.entries]
        return gen

    def write(self, path: GenPath, ctx: GenContext):
        target = self.compile()
        path.create(target)


@dataclass(frozen=True)
class RssEntry:
    id: str
    url: str
    title: str
    description: Optional[str]
    authors: Tuple[Author, ...]
    created: datetime
    updated: datetime

    def _as_fg(self):
        """Fill the provided FeedEntry with content."""
        feed_entry = fge.FeedEntry()
        feed_entry.id(self.id)
        feed_entry.link(href=self.url, rel='alternate')

        feed_entry.title(self.title)

        feed_entry.description(self.description)
        # TODO:mdrachuk:2019-09-02: support tags (categories)
        # TODO:mdrachuk:2019-09-02: support rich media (videos, audio)

        feed_entry.author(list(map(asdict, self.authors)))

        feed_entry.published(self.created)
        feed_entry.updated(self.updated)

        return feed_entry


@dataclass(frozen=True)
class AtomEntry:
    id: str
    url: str
    title: str
    summary: Optional[str]
    content: Optional[str]
    authors: Tuple[Author, ...]
    created: datetime
    updated: datetime

    def _as_fg(self) -> fge.FeedEntry:
        """Fill the provided FeedEntry with content."""
        feed_entry = fge.FeedEntry()

        feed_entry.id(self.id)
        feed_entry.link(href=self.url, rel='alternate')

        feed_entry.title(self.title)

        feed_entry.summary(self.summary)
        feed_entry.content(self.content)
        # TODO:mdrachuk:2019-09-02: support tags (categories)
        # TODO:mdrachuk:2019-09-02: support rich media (videos, audio)

        feed_entry.author(list(map(asdict, self.authors)))

        feed_entry.published(self.created)
        feed_entry.updated(self.updated)

        return feed_entry


T = TypeVar('T')


class EntryFactory(ABC, Generic[T]):

    @abstractmethod
    def rss(self, location: str, content: T, site: Site) -> RssEntry:
        """"""

    @abstractmethod
    def atom(self, location: str, content: T, site: Site) -> AtomEntry:
        """"""

    @abstractmethod
    def accepts(self, location: str, content: Content) -> bool:
        """"""


class MarkdownEntries(EntryFactory):

    def accepts(self, location: str, content: Content):
        return isinstance(content, MarkdownPage)

    def rss(self, location: str, content: MarkdownPage, site: Site) -> RssEntry:
        title = content.title or location
        description = content.summary or ''
        created = content.created or datetime.now(tz=timezone.utc)
        updated = content.updated or created
        return RssEntry(
            id=location,
            url=site / location,
            title=title,
            description=description,
            authors=tuple(site.authors),
            created=created,
            updated=updated,
        )

    def atom(self, location: str, content: MarkdownPage, site: Site) -> AtomEntry:
        title = content.title or location
        summary = content.summary or ''
        created = content.created or datetime.now(tz=timezone.utc)
        updated = content.updated or created
        return AtomEntry(
            id=location,
            url=site / location,
            title=title,
            summary=summary,
            content=None,
            authors=tuple(site.authors),
            created=created,
            updated=updated,
        )


class FeedGenerator:
    _factories: List[EntryFactory]

    def __init__(self):
        self._factories = []

    def _factory(self, location: str, content: Content):
        for factory in self._factories:
            if factory.accepts(location, content):
                return factory
        else:
            raise ValueError(f'Missing an Entry factory that can handle "{content}" at path "{location}"')

    def add_factory(self, factory: EntryFactory):
        self._factories.insert(0, factory)


class RssGenerator(FeedGenerator):
    def __call__(self, source: Site):
        """Create an RSS feed."""
        authors = tuple(source.authors)
        entries = [
            self._factory(ic.location, ic.content)
                .rss(ic.location, ic.content, source)
            for ic in source.content
        ]

        if not source.title or not source.description:
            raise ValueError('RSS feed requires a title and description.')

        return RssFeed(
            url=source.url,
            image_url=source.logo_url,
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
            self._factory(ic.location, ic.content)
                .atom(ic.location, ic.content, source)
            for ic in source.content
        ]
        if not source.title or not source.description:
            raise ValueError('Atom feed requires a title and description')

        return AtomFeed(
            url=source.url,
            icon_url=source.icon_url,
            logo_url=source.logo_url,
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
