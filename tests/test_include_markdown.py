from pathlib import Path

from lightweight import Site, markdown, template, directory, from_ctx


def test_render_markdown(tmp_path: Path):
    src_location = 'resources/md/collection/post-1.md'
    out_location = 'md/plain.html'

    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')

    site.add(out_location, markdown(src_location, template('templates/md/plain.html')))
    site.generate(test_out)

    assert (test_out / out_location).exists()
    with open('expected/md/plain.html') as expected:
        assert (test_out / out_location).read_text() == expected.read()


def test_render_toc(tmp_path: Path):
    src_location = 'resources/md/collection/post-1.md'
    out_location = 'md/toc.html'

    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')

    site.add(out_location, markdown(src_location, template('templates/md/toc.html')))
    site.generate(test_out)

    assert (test_out / out_location).exists()
    with open('expected/md/toc.html') as expected:
        assert (test_out / out_location).read_text() == expected.read()


def test_render_file(tmp_path: Path):
    src_location = 'resources/md/plain.md'
    out_location = 'md/file.html'

    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')

    site.add(out_location, markdown(src_location, template('templates/md/file.html')))
    site.generate(test_out)

    assert (test_out / out_location).exists()
    with open('expected/md/file.html') as expected:
        assert (test_out / out_location).read_text() == expected.read()


def test_render_markdown_link(tmp_path: Path):
    src_location = 'resources/md/link.md'
    link_target_location = 'resources/md/plain.md'
    out_location = 'md/file.html'

    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')

    site.add('plain.html', markdown(link_target_location, template('templates/md/plain.html')))
    site.add(out_location, markdown(src_location, template('templates/md/plain.html')))
    site.generate(test_out)

    assert (test_out / out_location).exists()
    with open('expected/md/md-link.html') as expected:
        assert (test_out / out_location).read_text() == expected.read()


def test_lazy_params(tmp_path: Path):
    src_location = 'resources/md/collection/post-1.md'
    out_location = 'lazy.html'

    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')

    site.add(out_location, markdown(src_location, template('templates/md/lazy.html'),
                                    lazy=from_ctx(lambda ctx: f'Hello there! {ctx.tasks[0].path}')))
    site.generate(test_out)

    assert (test_out / out_location).exists()
    with open('expected/md/lazy.html') as expected:
        assert (test_out / out_location).read_text() == expected.read()
