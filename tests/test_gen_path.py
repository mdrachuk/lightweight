from pathlib import Path

import pytest

from lightweight import Site, GenPath


def test_url(tmp_path: Path):
    site = Site('https://example.org/')
    url_factory = lambda location: site / location
    out = tmp_path

    page = GenPath(Path('page.html'), out, url_factory)
    index = GenPath(Path('index.html'), out, url_factory)
    style = GenPath(Path('style.css'), out, url_factory)

    assert style.url == 'https://example.org/style.css'
    assert page.url == 'https://example.org/page'
    assert index.url == 'https://example.org/'


def test_location(tmp_path: Path):
    site = Site('https://example.org/')
    url_factory = lambda location: site / location
    out = tmp_path

    page = GenPath(Path('page.html'), out, url_factory)
    index = GenPath(Path('index.html'), out, url_factory)
    style = GenPath(Path('style.css'), out, url_factory)

    assert style.location == 'style.css'
    assert page.location == 'page'
    assert index.location == ''


def test_parts(tmp_path: Path):
    site = Site('https://example.org/')
    url_factory = lambda location: site / location
    out = tmp_path

    page = GenPath(Path('something/page.html'), out, url_factory)
    index = GenPath(Path('index.html'), out, url_factory)

    assert page.parts == ('something', 'page.html')
    assert index.parts == ('index.html',)


def test_exists(tmp_path: Path):
    site = Site('https://example.org/')
    url_factory = lambda location: site / location
    out = tmp_path
    (tmp_path / 'yes.html').write_text('yea!')

    yes = GenPath(Path('yes.html'), out, url_factory)
    no = GenPath(Path('resources/test.html'), out, url_factory)

    assert yes.exists() is True
    assert no.exists() is False


def test_slash(tmp_path: Path):
    site = Site('https://example.org/')
    url_factory = lambda location: site / location
    out = tmp_path

    parent = GenPath(Path('parent'), out, url_factory)
    child1 = GenPath(Path('child1'), out, url_factory)
    child2 = Path('child2')
    child3 = 'child3'

    assert str(parent / child1) == 'parent/child1'
    assert str(parent / child2) == 'parent/child2'
    assert str(parent / child3) == 'parent/child3'

    bad_behaviour = 0
    with pytest.raises(ValueError):
        parent / bad_behaviour
