from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from sass import compile  # type: ignore # missing annotations

from lightweight.files import paths
from .content import Content
from ..generation import schedule

if TYPE_CHECKING:
    from lightweight import GenPath, GenContext


@dataclass(frozen=True)
class Sass(Content):
    """Content created by compiling Sass and SCSS."""
    path: Path
    sourcemap: bool

    async def write(self, path: GenPath, ctx: GenContext):
        if self.path.is_dir():
            css_at_target = construct_relative_css_path(self.path, target=path.absolute(), ctx=ctx)
            for p in paths(f'{self.path}/**/*.sass'):
                await _write(p, css_at_target(p), include_sourcemap=self.sourcemap)
            for p in paths(f'{self.path}/**/*.scss'):
                await _write(p, css_at_target(p), include_sourcemap=self.sourcemap)
        else:
            await _write(self.path, path, include_sourcemap=self.sourcemap)


def construct_relative_css_path(source: Path, *, target: Path, ctx: GenContext) -> Callable[[Path], GenPath]:
    start = len(source.parts)

    def remap(path: Path) -> GenPath:
        relative_parts = path.parts[start:]
        return ctx.path(Path(*target.parts, *relative_parts)).with_suffix('.css')

    return remap


async def _write(source: Path, target: GenPath, *, include_sourcemap: bool):
    sourcemap_path = target.with_name(target.name + '.map')
    result, sourcemap = compile(
        filename=str(source),
        source_map_filename=str(source.parent / sourcemap_path.name),
        source_map_root=str(source.parent),
        source_map_contents=True,
        output_style='compact',
    )
    await target.parent.a_mkdir()
    await target.a_create(result)
    if include_sourcemap:
        await sourcemap_path.a_create(sourcemap)


def sass(location: str, *, sourcemap: bool = True) -> Sass:
    """Run Sass/SCSS compiler on files at location. Can be a file name or a directory.

    @example
    Sourcemaps are written under "<location>.map".

    ```python
    site.include('css/style.css', sass('styles/style.scss'))
    ```
    Creates 2 files: `css/styles.css` and `css/styles.css.map`.
    """
    path = Path(location)
    if not path.exists():
        raise FileNotFoundError(f'Sass file not found: {location}')
    return Sass(path, sourcemap)
