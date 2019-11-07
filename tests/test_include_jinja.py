from pathlib import Path

import pytest

from lightweight import Site, render
from lightweight.content import Content
from lightweight.errors import NoSourcePath


def test_render_jinja(tmp_path: Path):
    src_location = 'resources/jinja/title.html'
    out_location = 'title.html'

    test_out = tmp_path / 'out'
    site = Site(url='https://example.com', out=test_out)

    site.include(out_location, render(src_location, title='99 reasons lightweight rules'))
    site.render()

    assert (test_out / out_location).exists()
    with open('expected/jinja/params.html') as expected:
        assert (test_out / out_location).read_text() == expected.read()


def test_render_jinja_shortcut(tmp_path: Path):
    location = 'resources/jinja/title.html'

    test_out = tmp_path / 'out'
    site = Site(url='https://example.com', out=test_out)

    site.include(render(location, title='99 reasons lightweight rules'))
    site.render()

    assert (test_out / location).exists()
    with open('expected/jinja/params.html') as expected:
        assert (test_out / location).read_text() == expected.read()


def test_render_jinja_file(tmp_path: Path):
    src_location = 'resources/jinja/file.html'
    out_location = 'jinja/file.html'

    test_out = tmp_path / 'out'
    site = Site(url='https://example.com', out=test_out)

    site.include(out_location, render(src_location))
    site.render()

    assert (test_out / out_location).exists()
    with open('expected/jinja/file.html') as expected:
        assert (test_out / out_location).read_text() == expected.read()


class NoopContent(Content):
    def write(self, path: Path):
        """"""


def test_render_missing_jinja_shortcut(tmp_path: Path):
    site = Site(url='https://example.com', out=tmp_path / 'out')
    with pytest.raises(NoSourcePath):
        site.include(NoopContent())
