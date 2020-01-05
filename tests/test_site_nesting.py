from pathlib import Path

from lightweight import Site
from lightweight.content.copy import FileCopy


def test_include_site(tmp_path: Path):
    test_out = Path(tmp_path)
    src_location = 'resources/test.html'
    with Path(src_location).open() as f:
        src_content = f.read()

    root = Site('http://example.org')

    child = Site('http://example.org/child')
    child.include('test.html', FileCopy(src_location))

    root.include('child', child)

    root.generate(tmp_path)
    assert (test_out / 'child/test.html').exists()
    assert (test_out / 'child/test.html').read_text() == src_content
