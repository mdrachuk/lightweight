from pathlib import Path

from lightweight import paths


def test_dir():
    assert set(paths('glob-resources')) == {Path('glob-resources')}


def test_file():
    assert set(paths('glob-resources/a.md')) == {Path('glob-resources/a.md')}


def test_files():
    assert set(paths('glob-resources/*.html')) == {Path('glob-resources/a.html'),
                                                   Path('glob-resources/b.html')}


def test_recursive_files():
    assert set(paths('glob-resources/**/*.md')) == {Path('glob-resources/a.md'),
                                                    Path('glob-resources/b.md'),
                                                    Path('glob-resources/dir/1.md')}
