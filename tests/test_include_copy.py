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
    site = Site(url='https://example.com')

    site.include(src_location)
    site.render(test_out)

    assert (test_out / src_location).exists()
    assert (test_out / src_location).read_text() == src_content


def test_include_not_found(tmp_path: Path):
    site = Site(url='https://example.com')

    with pytest.raises(FileNotFoundError):
        site.include(str(uuid4()))


def test_include_directory(tmp_path: Path):
    src_location = 'resources/test_nested/test2/test3/test.html'
    src_path = Path(src_location)
    with src_path.open() as f:
        src_content = f.read()

    test_out = tmp_path / 'out'
    site = Site(url='https://example.com')

    site.include('resources/test_nested')
    site.render(test_out)

    assert (test_out / src_location).exists()
    assert (test_out / src_location).read_text() == src_content


def test_include_glob(tmp_path: Path):
    test_out = tmp_path / 'out'
    site = Site(url='https://example.com')
    site.include('resources/glob/**/*.html')
    site.render(test_out)
    result = test_out / 'resources' / 'glob'
    assert (result / 'a.html').exists()
    assert (result / 'b.html').exists()
    assert (result / 'dir' / '1.html').exists()
