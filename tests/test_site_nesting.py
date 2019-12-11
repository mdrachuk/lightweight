from pathlib import Path

from lightweight import Site


def test_include_site(tmp_path: Path):
    test_out = Path(tmp_path)
    src_location = 'resources/test.html'
    with Path(src_location).open() as f:
        src_content = f.read()

    child = Site()
    child.include(src_location)

    root = Site()
    root.include('/child', child)

    root.render(tmp_path)
    assert (test_out / src_location).exists()
    assert (test_out / src_location).read_text() == src_content
