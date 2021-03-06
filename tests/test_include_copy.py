from pathlib import Path
from uuid import uuid4

import pytest

from lightweight import Site


def test_include_file(tmp_path: Path):
    src_location = 'resources/test.html'
    src_path = Path(src_location)
    with src_path.open() as f:
        src_content = f.read()

    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')

    site.add(src_location)
    site.generate(test_out)

    assert (test_out / src_location).exists()
    assert (test_out / src_location).read_text() == src_content


def test_include_not_found(tmp_path: Path):
    site = Site(url='https://example.org/')

    with pytest.raises(FileNotFoundError):
        site.add(str(uuid4()))


def test_include_directory(tmp_path: Path):
    src_location = 'resources/test_nested/test2/test3/test.html'
    src_path = Path(src_location)
    with src_path.open() as f:
        src_content = f.read()

    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')

    site.add('resources/test_nested')
    site.generate(test_out)

    assert (test_out / src_location).exists()
    assert (test_out / src_location).read_text() == src_content


def test_include_glob(tmp_path: Path):
    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')
    site.add('resources/glob/**/*.html')
    site.generate(test_out)
    result = test_out / 'resources' / 'glob'
    assert (result / 'a.html').exists()
    assert (result / 'b.html').exists()
    assert (result / 'dir' / '1.html').exists()


def test_include_file_under_different_name(tmp_path: Path):
    src_location = 'resources/test.html'
    src_path = Path(src_location)
    with src_path.open() as f:
        src_content = f.read()

    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')

    site.add('a.html', src_location)
    site.generate(test_out)

    assert (test_out / 'a.html').exists()
    assert (test_out / 'a.html').read_text() == src_content


def test_include_dir_under_different_name(tmp_path: Path):
    src_location = 'resources/test_nested/test2/test3/test.html'
    src_path = Path(src_location)
    with src_path.open() as f:
        src_content = f.read()

    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')

    site.add('successful_test', 'resources/test_nested')
    site.generate(test_out)

    assert (test_out / 'successful_test/test2/test3/test.html').exists()
    assert (test_out / 'successful_test/test2/test3/test.html').read_text() == src_content


def test_include_not_found_under_different_name(tmp_path: Path):
    site = Site(url='https://example.org/')

    with pytest.raises(FileNotFoundError):
        site.add('t.html', str(uuid4()))
