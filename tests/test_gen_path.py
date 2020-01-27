from pathlib import Path

from lightweight import Site, GenPath


def test_gen_path_url(tmp_path: Path):
    site = Site('https://example.org/')
    url_factory = lambda location: site / location
    out = tmp_path

    page = GenPath(Path('page.html'), out, url_factory)
    index = GenPath(Path('index.html'), out, url_factory)
    style = GenPath(Path('style.css'), out, url_factory)

    assert style.url == 'https://example.org/style.css'
    assert page.url == 'https://example.org/page'
    assert index.url == 'https://example.org/'


def test_gen_path_location(tmp_path: Path):
    site = Site('https://example.org/')
    url_factory = lambda location: site / location
    out = tmp_path

    page = GenPath(Path('page.html'), out, url_factory)
    index = GenPath(Path('index.html'), out, url_factory)
    style = GenPath(Path('style.css'), out, url_factory)

    assert style.location == 'style.css'
    assert page.location == 'page'
    assert index.location == ''