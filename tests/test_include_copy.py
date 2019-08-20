from pathlib import Path
from uuid import uuid4

import pytest

from lightweight import Site


def test_include_file(tmp_path: Path):
    src_location = 'resources/test.html'
    src_path = Path(src_location)
    with src_path.open() as f:
        src_content = f.read()

    out_path = tmp_path / 'out'
    site = Site(out_path)

    site.include(src_location)
    site.render()

    assert (out_path / src_location).exists()
    assert (out_path / src_location).read_text() == src_content


def test_include_not_found(tmp_path: Path):
    out_path = tmp_path / 'out'
    site = Site(out_path)

    with pytest.raises(FileNotFoundError):
        site.include(str(uuid4()))


def test_include_directory(tmp_path: Path):
    src_location = 'resources/test1/test2/test3/test.html'
    src_path = Path(src_location)
    with src_path.open() as f:
        src_content = f.read()

    out_path = tmp_path / 'out'
    site = Site(out_path)

    site.include('resources/test1')
    site.render()

    assert (out_path / src_location).exists()
    assert (out_path / src_location).read_text() == src_content
