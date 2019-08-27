from pathlib import Path

from lightweight import Site, markdown, template


def test_render_markdown(tmp_path: Path):
    src_location = 'resources/md/collection/post-1.md'
    out_location = 'md/plain.html'

    out_path = tmp_path / 'out'
    site = Site(out_path)

    site.include(out_location, markdown(src_location, template('md/plain.html')))
    site.render()

    assert (out_path / out_location).exists()
    with open('expected/md/plain.html') as expected:
        assert (out_path / out_location).read_text() == expected.read()


def test_render_toc(tmp_path: Path):
    src_location = 'resources/md/collection/post-1.md'
    out_location = 'md/toc.html'

    out_path = tmp_path / 'out'
    site = Site(out_path)

    site.include(out_location, markdown(src_location, template('md/toc.html')))
    site.render()

    assert (out_path / out_location).exists()
    with open('expected/md/toc.html') as expected:
        assert (out_path / out_location).read_text() == expected.read()


def test_render_file(tmp_path: Path):
    src_location = 'resources/md/plain.md'
    out_location = 'md/file.html'

    out_path = tmp_path / 'out'
    site = Site(out_path)

    site.include(out_location, markdown(src_location, template('md/file.html')))
    site.render()

    assert (out_path / out_location).exists()
    with open('expected/md/file.html') as expected:
        assert (out_path / out_location).read_text() == expected.read()
