from pathlib import Path

import pytest

from lightweight import Site
from lightweight.errors import AbsolutePathIncluded


def test_rewrite_out(tmp_path: Path):
    assert_site_render('resources/test_nested/test2/test3/test.html', 'resources/test_nested', tmp_path)
    assert_site_render('resources/test.html', 'resources/test.html', tmp_path)


def assert_site_render(src_location, content, tmp_path):
    with Path(src_location).open() as f:
        src_content = f.read()
    test_out = tmp_path / 'out'
    site = Site(url='https://example.com')
    site.include(content)
    site.render(test_out)
    assert (test_out / src_location).exists()
    assert (test_out / src_location).read_text() == src_content


def test_absolute_includes_not_allowed():
    site = Site('http://example.org')
    with pytest.raises(AbsolutePathIncluded):
        site.include('/etc')


def test_site_location(tmp_path: Path):
    site = Site(url='http://example.org')
    assert site / 'test.html' == 'http://example.org/test.html'
    assert site / '/test.html' == 'http://example.org/test.html'
    assert site / '/foo/bar' == 'http://example.org/foo/bar'
