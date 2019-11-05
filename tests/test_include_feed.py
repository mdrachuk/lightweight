from datetime import datetime, timezone, timedelta
from pathlib import Path

from lightweight import Site, markdown, template, paths, atom, rss

PDT = timezone(timedelta(hours=-7))
apr_20 = datetime(2020, 4, 20, 16, 20, tzinfo=PDT)


def md_posts(location):
    return (markdown(path, template('md/plain.html')) for path in paths(location))


def test_create_atom(tmp_path: Path):
    test_out = tmp_path / 'out'
    site = Site(url='https://example.com', out=test_out, title='Tests')
    site.updated = apr_20

    [site.include(f'posts/{md.filename.stem}.html', md) for md in md_posts('resources/md/collection/*.md')]
    posts = atom(site['posts'])
    site.include('posts.atom.xml', posts)

    site.render()

    assert (test_out / 'posts.atom.xml').exists()
    with open('expected/feed/posts.atom.xml') as expected:
        assert (test_out / 'posts.atom.xml').read_text() == expected.read()


def test_create_rss(tmp_path: Path):
    test_out = tmp_path / 'out'
    site = Site(url='https://example.com', out=test_out, title='Tests')
    site.updated = apr_20

    [site.include(f'posts/{md.filename.stem}.html', md) for md in md_posts('resources/md/collection/*.md')]
    posts = rss(site['posts'])
    site.include('posts.rss.xml', posts)

    site.render()

    assert (test_out / 'posts.rss.xml').exists()
    with open('expected/feed/posts.rss.xml') as expected:
        assert (test_out / 'posts.rss.xml').read_text() == expected.read()
