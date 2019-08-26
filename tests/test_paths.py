from pathlib import Path

from lightweight import paths


def test_dir():
    assert set(paths('resources/glob')) == {Path('resources/glob')}


def test_file():
    assert set(paths('resources/glob/a.md')) == {Path('resources/glob/a.md')}


def test_files():
    assert set(paths('resources/glob/*.html')) == {Path('resources/glob/a.html'),
                                                   Path('resources/glob/b.html')}


def test_recursive_files():
    assert set(paths('resources/glob/**/*.md')) == {Path('resources/glob/a.md'),
                                                    Path('resources/glob/b.md'),
                                                    Path('resources/glob/dir/1.md')}


def test_path():
    assert set(paths(Path('resources/test.html'))) == {Path('resources/test.html')}
