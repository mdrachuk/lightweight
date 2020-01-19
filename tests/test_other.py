from pathlib import Path

import pytest
from jinja2 import UndefinedError

from lightweight import Site, Author, GenPath, jinja_env
from lightweight.errors import AbsolutePathIncluded


def test_rewrite_out(tmp_path: Path):
    assert_site_render('resources/test_nested/test2/test3/test.html', 'resources/test_nested', tmp_path)
    assert_site_render('resources/test.html', 'resources/test.html', tmp_path)


def assert_site_render(src_location, content, tmp_path):
    with Path(src_location).open() as f:
        src_content = f.read()
    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')
    site.include(content)
    site.generate(test_out)
    assert (test_out / src_location).exists()
    assert (test_out / src_location).read_text() == src_content


def test_absolute_includes_not_allowed():
    site = Site('https://example.org/')
    with pytest.raises(AbsolutePathIncluded):
        site.include('/etc')


def test_site_location(tmp_path: Path):
    site = Site(url='https://example.org/')
    assert site / 'test.html' == 'https://example.org/test.html'
    assert site / '/test.html' == 'https://example.org/test.html'
    assert site / '/foo/bar' == 'https://example.org/foo/bar'


def test_site_single_author():
    name = 'Test'
    email = 'test@example.org'
    site = Site(url='https://example.org/', author_name=name, author_email=email)
    assert site.authors == {Author(name, email)}


def test_site_multiple_authors():
    site = Site(url='https://example.org/', authors=[
        Author('a', 'a@example.org'),
        Author('b', 'b@example.org'),
        Author('c', 'c@example.org')
    ])
    assert site.authors == {Author('a', 'a@example.org'),
                            Author('b', 'b@example.org'),
                            Author('c', 'c@example.org')}


def test_site_authors_combination():
    name = 'Test'
    email = 'test@example.org'
    site = Site(
        url='https://example.org/',
        author_name=name,
        author_email=email,
        authors=[
            Author('a', 'a@example.org'),
            Author('b', 'b@example.org'),
            Author('c', 'c@example.org')
        ]
    )
    assert site.authors == {Author(name, email),
                            Author('a', 'a@example.org'),
                            Author('b', 'b@example.org'),
                            Author('c', 'c@example.org')}


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


def test_jinja_env_does_not_allow_undefined():
    with pytest.raises(UndefinedError):
        jinja_env.from_string('{{something}}').render()
