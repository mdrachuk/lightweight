from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path, PurePath
from typing import Callable, Tuple, Union, IO, Any

UrlFactory = Callable[[str], str]  # A url factory a full URL with a provided relative location.


@dataclass(frozen=True)
class GenPath:
    """A path for [writing content][lightweight.content.Content.write].
    It contains both, the relative path (as specified by `site.add(relative_path, content)`)
    and the real path (an absolute path which in site’s `out`).

    File system operations performed on real_path; relative path is used for all other operations,
    e.g. `__str__` returns a relative path representation.

    Also, proper URL can be obtained from [generation path][GenPath]

    ```
    site = Site('https://example.org/')
    resources = GenPath(Path('resources'), out='/tmp/out', url_factory=lambda location: site/location)

    teapot: GenPath = resources / 'teapot.txt'

    print(str(teapot))  # resources/teapot.txt
    print(teapot.absolute())  # '/tmp/out/resources/teapot.txt'
    print(teapot.url)  # https://example.org/resources/teapot.txt

    print(teapot.exists())  # False

    # Create a file with text.
    teapot.create('I am a teapot')

    print(teapot.exists())  # True
    ```
    """
    relative_path: Path
    out: Path
    url_factory: UrlFactory

    @property
    def real_path(self) -> Path:
        """An absolute path of the file in the generation out directory."""
        return (self.out / self.relative_path).absolute()

    @property
    def name(self) -> str:
        """The name of the file at path."""
        return self.relative_path.name

    @property
    def parts(self) -> Tuple[str, ...]:
        """Split the path in parts."""
        return self.relative_path.parts

    @property
    def parent(self) -> GenPath:
        """Get a [GenPath] of a parent directory."""
        return replace(self, relative_path=self.relative_path.parent)

    @property
    def suffix(self) -> str:
        """An extension of the file."""
        return self.relative_path.suffix

    @property
    def url(self) -> str:
        """Create a URL for file at path.

        URL is created by a URL factory. By default this would

        ```
        site = Site('https://example.org/')
        url_factory = lambda location: site/location
        out = '/tmp/out'

        page = GenPath(Path('page.html'), out, url_factory)
        index = GenPath(Path('index.html'), out, url_factory)
        style = GenPath(Path('style.css'), out, url_factory)

        print(style.url)  # https://example.org/style.css
        print(page.url)  # https://example.org/page
        print(index.url)  # https://example.org/
        ```
        """
        return self.url_factory(self.location)  # type: ignore # Invalid self argument mypy error

    @property
    def location(self) -> str:
        """A string representation of relative path stripping `index.html` or `.html` from the end.
        This means that:
        - `css/style.css` stays the same;
        - `shop/products/index.html` becomes `shop/products/`;
        - and `/blog/posts/zen-of-python.html` becomes `/blog/posts/zen-of-python`;
        """
        if self.name == 'index.html':
            loc = self.parent
        elif self.suffix == '.html':
            loc = self.with_suffix('')
        else:
            loc = self
        as_string = str(loc)
        if as_string == '.':
            return ''
        return as_string

    def absolute(self) -> Path:
        """An alias of [GenPath.real_path]."""
        return self.real_path

    def exists(self) -> bool:
        """Checks if file exists"""
        return self.real_path.exists()

    def mkdir(self, mode=0o777, parents=True, exist_ok=True):
        """Create directory at path.

        Differs from the defaults in other Python mkdir signatures:
        creates whole parent hierarchy of directories if they do not exist.
        """
        return self.real_path.mkdir(mode=mode, parents=parents, exist_ok=exist_ok)

    def __truediv__(self, other: Union[GenPath, PurePath, str]) -> GenPath:
        """A child generation path can be created from an existing one by using division operator.

        ```python
        parent = GenPath(Path('something/', 'tmp/out, ...))
        child = parent / 'child'
        print(repr(child))  GenPath(relative_path=PosixPath('something/child'), out='/tmp/out', ...)
        ```
        """
        other_path: Union[PurePath, str]
        if isinstance(other, GenPath):
            other_path = other.relative_path
        elif isinstance(other, PurePath) or isinstance(other, str):
            other_path = other
        else:
            raise ValueError(f'Cannot make a path with {other}')
        return replace(self, relative_path=self.relative_path / other_path)

    def __str__(self) -> str:
        return str(self.relative_path)

    def with_name(self, name: str) -> GenPath:
        """Create a new [GenPath] which differs from the current only by file name."""
        return replace(self, relative_path=self.relative_path.with_name(name))

    def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None) -> IO[Any]:
        """Open the file. Same as [Path.open(...)][Path.open]"""
        return self.real_path.open(mode=mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline)

    def with_suffix(self, suffix: str) -> GenPath:
        """Create a new [GenPath] with a different file suffix (extension)."""
        return replace(self, relative_path=self.relative_path.with_suffix(suffix))

    def create(self, contents: Union[str, bytes]) -> None:
        """Create a file with provided contents. Contents can be `str` or `bytes`."""
        self.parent.mkdir()
        binary_mode = isinstance(contents, bytes)
        with self.open('wb' if binary_mode else 'w') as f:
            f.write(contents)  # type: ignore
