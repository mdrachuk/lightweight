from pathlib import Path

from lightweight import Site, directory
from lightweight.content.copies import FileCopy


def test_include_site(tmp_path: Path):
    test_out = Path(tmp_path)
    src_location = 'resources/test.html'
    with Path(src_location).open() as f:
        src_content = f.read()

    root = Site('https://example.org/')

    child = Site('https://example.org/child/')
    child.include('test.html', FileCopy(src_location))

    root.include('child', child)

    root.generate(tmp_path)
    assert (test_out / 'child/test.html').exists()
    assert (test_out / 'child/test.html').read_text() == src_content


def test_subsite_cwd_change(tmp_path: Path):
    site = Site('https://example.org/')
    site.include('index.html', 'site/index.html')
    with directory('site'):
        subsite = Site('https://example.org/')
        subsite.include('file')
    site.include('subsite', subsite)
    site.generate(out=tmp_path)
