from pathlib import Path

import pytest

from lightweight import Site, sass


def test_render_scss_file(tmp_path: Path):
    src_location = 'resources/scss/style.scss'
    out_location = 'css/style.css'

    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')

    site.include(out_location, sass(src_location))
    site.generate(test_out)

    assert (test_out / out_location).exists()
    with open('expected/scss/style.css') as expected:
        assert (test_out / out_location).read_text() == expected.read()


def test_render_scss_directory(tmp_path: Path):
    src_location = 'resources/scss/styles'
    out_location = 'css/nested'

    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')

    site.include(out_location, sass(src_location))
    site.generate(test_out)

    assert (test_out / out_location).exists()
    with open('expected/scss/nested/test1.css') as expected:
        assert (test_out / 'css/nested/test1.css').read_text() == expected.read()
    with open('expected/scss/nested/nested/test2.css') as expected:
        assert (test_out / 'css/nested/nested/test2.css').read_text() == expected.read()


def test_render_sass_directory(tmp_path: Path):
    src_location = 'resources/sass/styles'
    out_location = 'css/nested'

    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')

    site.include(out_location, sass(src_location))
    site.generate(test_out)

    assert (test_out / out_location).exists()
    with open('expected/sass/nested/test1.css') as expected:
        assert (test_out / 'css/nested/test1.css').read_text() == expected.read()
    with open('expected/sass/nested/nested/test2.css') as expected:
        assert (test_out / 'css/nested/nested/test2.css').read_text() == expected.read()


def test_nonexistent(tmp_path: Path):
    src_location = 'resources/scss/test.scss'
    site = Site(url='https://example.org/')

    with pytest.raises(FileNotFoundError):
        site.include('', sass(src_location))


def test_render_scss_file_sourcemaps(tmp_path: Path):
    src_location = 'resources/scss/style.scss'
    out_location = 'css/style.css'

    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')

    site.include(out_location, sass(src_location))
    site.generate(test_out)

    with open('expected/scss/style.css.map') as expected:
        assert (test_out / 'css/style.css.map').read_text() == expected.read()


def test_render_scss_directory_sourcemaps(tmp_path: Path):
    src_location = 'resources/scss/styles'
    out_location = 'css'

    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')

    site.include(out_location, sass(src_location))
    site.generate(test_out)

    with open('expected/scss/nested/test1.css.map') as expected:
        assert (test_out / 'css/test1.css.map').read_text() == expected.read()
    with open('expected/scss/nested/nested/test2.css.map') as expected:
        assert (test_out / 'css/nested/test2.css.map').read_text() == expected.read()
