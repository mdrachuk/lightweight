from pathlib import Path

import pytest
from jinja2.utils import LRUCache

from lightweight import Site, Author, GenPath
from lightweight.errors import AbsolutePathIncluded
from lightweight.template import LruCachePerCwd


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


def test_package():
    pass


def test_per_cwd_jinja_cache_creation():
    cache = LruCachePerCwd(100)
    jlru = cache.instance()
    assert isinstance(jlru, LRUCache)
    assert jlru.capacity == 100


class CallRecorder:
    def __getattr__(self, name):
        self.last_access = name
        return self.save_params

    def save_params(self, *args, **kwargs):
        self.la_args = args
        self.la_kwargs = kwargs

    def __repr__(self):
        self.last_access = '__repr__'
        self.la_args = []
        self.la_kwargs = {}


class MockCache(LruCachePerCwd):
    def __init__(self, recorder: CallRecorder):
        super().__init__(100)
        self.recorder = recorder

    def instance(self):
        return self.recorder


def test_per_cwd_jinja_cache_calls():
    cr = CallRecorder()
    cache = MockCache(cr)
    cache.__getstate__(1, a='a', b='b')
    assert cr.last_access == '__getstate__'

    cache.__setstate__(1, a='a', b='b')
    assert cr.last_access == '__setstate__'

    cache.__getnewargs__(1, a='a', b='b')
    assert cr.last_access == '__getnewargs__'

    cache.copy(1, a='a', b='b')
    assert cr.last_access == 'copy'

    cache.get(1, a='a', b='b')
    assert cr.last_access == 'get'

    cache.setdefault(1, a='a', b='b')
    assert cr.last_access == 'setdefault'

    cache.clear(1, a='a', b='b')
    assert cr.last_access == 'clear'

    cache.__contains__(1, a='a', b='b')
    assert cr.last_access == '__contains__'

    cache.__len__(1, a='a', b='b')
    assert cr.last_access == '__len__'

    cache.__repr__()
    assert cr.last_access == '__repr__'

    cache.__getitem__(1, a='a', b='b')
    assert cr.last_access == '__getitem__'

    cache.__setitem__(1, a='a', b='b')
    assert cr.last_access == '__setitem__'

    cache.__delitem__(1, a='a', b='b')
    assert cr.last_access == '__delitem__'

    cache.items(1, a='a', b='b')
    assert cr.last_access == 'items'

    cache.iteritems(1, a='a', b='b')
    assert cr.last_access == 'iteritems'

    cache.values(1, a='a', b='b')
    assert cr.last_access == 'values'

    cache.itervalue(1, a='a', b='b')
    assert cr.last_access == 'itervalue'

    cache.keys(1, a='a', b='b')
    assert cr.last_access == 'keys'

    cache.iterkeys(1, a='a', b='b')
    assert cr.last_access == 'iterkeys'

    cache.__reversed__(1, a='a', b='b')
    assert cr.last_access == '__reversed__'

    cache.__iter__(1, a='a', b='b')
    assert cr.last_access == '__iter__'

    cache.__copy__(1, a='a', b='b')
    assert cr.last_access == '__copy__'
