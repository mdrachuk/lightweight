from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from sass import compile  # type: ignore # missing annotations

from lightweight.files import paths
from .content import Content

if TYPE_CHECKING:
    from lightweight import RenderPath


@dataclass(frozen=True)
class Sass(Content):
    path: Path
    sourcemap: bool

    def write(self, path: RenderPath):
        if self.path.is_dir():
            css_at_target = construct_relative_css_path(self.path, target=path)
            for p in paths(f'{self.path}/**/*.sass'):
                _render(p, css_at_target(p), include_sourcemap=self.sourcemap)
            for p in paths(f'{self.path}/**/*.scss'):
                _render(p, css_at_target(p), include_sourcemap=self.sourcemap)
        else:
            _render(self.path, path, include_sourcemap=self.sourcemap)


def construct_relative_css_path(source: Path, *, target: RenderPath) -> Callable[[Path], RenderPath]:
    start = len(source.parts)

    def remap(path: Path) -> RenderPath:
        relative_parts = path.parts[start:]
        return target.ctx.path(Path(*target.parts, *relative_parts)).with_suffix('.css')

    return remap


def _render(source: Path, target: RenderPath, *, include_sourcemap: bool):
    sourcemap_path = target.with_name(target.name + '.map')
    result, sourcemap = compile(
        filename=str(source),
        source_map_filename=str(source.parent / sourcemap_path.name),
        source_map_root=str(source.parent),
        source_map_contents=True,
        output_style='compact',
    )
    target.parent.mkdir()
    with target.open('w') as css_file:
        css_file.write(result)
    if include_sourcemap:
        with sourcemap_path.open('w') as sourcemap_file:
            sourcemap_file.write(sourcemap)


def sass(location: str, *, sourcemap=True) -> Sass:
    path = Path(location)
    if not path.exists():
        raise FileNotFoundError(f'Sass file not found: {location}')
    return Sass(path, sourcemap)
