from pathlib import Path

from lightweight import Site


def test_rewrite_out(tmp_path: Path):
    assert_site_render('resources/test_nested/test2/test3/test.html', 'resources/test_nested', tmp_path)
    assert_site_render('resources/test.html', 'resources/test.html', tmp_path)


def assert_site_render(src_location, include, tmp_path):
    with Path(src_location).open() as f:
        src_content = f.read()
    test_out = tmp_path / 'out'
    site = Site(url='https://example.com', out=test_out)
    site.include(include)
    site.render()
    assert (test_out / src_location).exists()
    assert (test_out / src_location).read_text() == src_content
