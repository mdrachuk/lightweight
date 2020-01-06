from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urljoin

import pytest

from lightweight import Site, markdown, template, paths, atom, rss, Content, GenPath
from lightweight.content.feeds import RssGenerator, EntryFactory, AtomEntry, RssEntry, AtomGenerator

PDT = timezone(timedelta(hours=-7))
apr_20 = datetime(2020, 4, 20, 16, 20, tzinfo=PDT)


def md_posts(location):
    return (markdown(path, template('templates/md/plain.html')) for path in paths(location))


def test_create_atom(tmp_path: Path):
    test_out = tmp_path / 'out'
    site = Site(url='https://example.com', title='Tests', description='Test site', updated=apr_20)

    [site.include(f'posts/{md.source_path.stem}.html', md) for md in md_posts('resources/md/collection/*.md')]
    site.include('posts.atom.xml', atom(site['posts']))

    site.generate(test_out)

    assert (test_out / 'posts.atom.xml').exists()
    with open('expected/feed/posts.atom.xml') as expected:
        assert (test_out / 'posts.atom.xml').read_text() == expected.read()


def test_create_rss(tmp_path: Path):
    test_out = tmp_path / 'out'
    site = Site(url='https://example.com', title='Tests', description='Test site', updated=apr_20)

    [site.include(f'posts/{md.source_path.stem}.html', md) for md in md_posts('resources/md/collection/*.md')]
    site.include('posts.rss.xml', rss(site['posts']))

    site.generate(test_out)

    assert (test_out / 'posts.rss.xml').exists()
    with open('expected/feed/posts.rss.xml') as expected:
        assert (test_out / 'posts.rss.xml').read_text() == expected.read()


@dataclass(frozen=True)
class Symbol(Content):
    value: str

    def write(self, path: GenPath, ctx):
        path.create(self.value)


class SymbolEntries(EntryFactory[Symbol]):

    def rss(self, location: str, content: Symbol, site: Site) -> RssEntry:
        url = urljoin(site.url, location)
        return RssEntry(
            id=location,
            url=url,
            title=content.value.upper(),
            description=content.value,
            authors=tuple(),
            created=apr_20,
            updated=apr_20,
        )

    def atom(self, location: str, content: Symbol, site: Site) -> AtomEntry:
        url = urljoin(site.url, location)
        return AtomEntry(
            id=location,
            url=url,
            title=content.value.upper(),
            summary=content.value,
            content=None,
            authors=tuple(),
            created=apr_20,
            updated=apr_20,
        )

    def accepts(self, location: str, content: Content) -> bool:
        return isinstance(content, Symbol)


def test_custom_content_errors(tmp_path):
    site = Site(url='https://example.com', title='Tests', description='Test site')

    [site.include(s, Symbol(s)) for s in 'abcdefghijklmnopqrstvuwxyz']
    with pytest.raises(ValueError):
        site.include('symbols.rss.xml', rss(site))
    with pytest.raises(ValueError):
        site.include('symbols.atom.xml', atom(site))


def test_custom_content_factory(tmp_path):
    test_out = tmp_path / 'out'
    site = Site(url='https://example.com', title='Tests', description='Test site', updated=apr_20)

    [site.include(f'symbols/{s}', Symbol(s)) for s in 'abcdefghijklmnopqrstvuwxyz']
    _symbol_entry_factory = SymbolEntries()
    my_rss = RssGenerator()
    my_rss.add_factory(_symbol_entry_factory)
    my_atom = AtomGenerator()
    my_atom.add_factory(_symbol_entry_factory)

    site.include('symbols.rss.xml', my_rss(site['symbols']))
    site.include('symbols.atom.xml', my_atom(site['symbols']))

    site.generate(test_out)

    assert (test_out / 'symbols.rss.xml').exists()
    assert (test_out / 'symbols.atom.xml').exists()
    with open('expected/feed/symbols.rss.xml') as expected:
        assert (test_out / 'symbols.rss.xml').read_text() == expected.read()
    with open('expected/feed/symbols.atom.xml') as expected:
        assert (test_out / 'symbols.atom.xml').read_text() == expected.read()
