from pathlib import Path

from lightweight import Site, markdown


def test_render_markdown(tmp_path: Path):
    src_location = 'resources/collection/post-1.md'
    out_location = 'plain-md.html'

    out_path = tmp_path / 'out'
    site = Site(out_path)

    site.include(out_location, markdown(src_location, site.template('plain-md.html')))
    site.render()

    assert (out_path / out_location).exists()
    with open('expected/plain-md.html') as expected:
        assert (out_path / out_location).read_text() == expected.read()


def test_render_toc(tmp_path: Path):
    src_location = 'resources/collection/post-1.md'
    out_location = 'md-toc.html'

    out_path = tmp_path / 'out'
    site = Site(out_path)

    site.include(out_location, markdown(src_location, site.template('md-toc.html')))
    site.render()

    assert (out_path / out_location).exists()
    with open('expected/md-toc.html') as expected:
        assert (out_path / out_location).read_text() == expected.read()
