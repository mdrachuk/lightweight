from pathlib import Path

import pytest

from lightweight import Site, sass


def test_render_scss_file(tmp_path: Path):
    src_location = 'resources/sass/style.scss'
    out_location = 'css'

    out = tmp_path / 'out'
    site = Site(out)

    site.include(out_location, sass(src_location))
    site.render()

    assert (out / out_location).exists()
    with open('expected/sass/style.css') as expected:
        assert (out / out_location).read_text() == expected.read()


def test_render_scss_directory(tmp_path: Path):
    src_location = 'resources/sass/styles'
    out_location = 'css'

    out = tmp_path / 'out'
    site = Site(out)

    site.include(out_location, sass(src_location))
    site.render()

    assert (out / out_location).exists()
    with open('expected/sass/nested/test1.css') as expected:
        assert (out / 'css/nested/test1.css').read_text() == expected.read()
    with open('expected/sass/nested/nested/test2.css') as expected:
        assert (out / 'css/nested/nested/test2.css').read_text() == expected.read()


def test_nonexistent(tmp_path: Path):
    src_location = 'resources/sass/test.scss'
    site = Site(tmp_path / 'out')

    with pytest.raises(FileNotFoundError):
        site.include('', sass(src_location))


def test_render_scss_file_sourcemaps(tmp_path: Path):
    src_location = 'resources/sass/style.scss'
    out_location = 'css/style.css'

    out = tmp_path / 'out'
    site = Site(out)

    site.include(out_location, sass(src_location))
    site.render()

    with open('expected/sass/style.css.map') as expected:
        assert (out / 'css/style.css.map').read_text() == expected.read()


def test_render_scss_directory_sourcemaps(tmp_path: Path):
    src_location = 'resources/sass/styles'
    out_location = 'css'

    out = tmp_path / 'out'
    site = Site(out)

    site.include(out_location, sass(src_location))
    site.render()

    with open('expected/sass/nested/tes1.css.map') as expected:
        assert (out / 'css/nested/test1.css.map').read_text() == expected.read()
    with open('expected/sass/nested/nested/test2.css.map') as expected:
        assert (out / 'css/nested/nested/test2.css.map').read_text() == expected.read()
