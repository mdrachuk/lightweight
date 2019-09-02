from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from sass import compile  # type: ignore # missing annotations

from lightweight.files import paths
from .content import Content

if TYPE_CHECKING:
    from lightweight import SitePath


@dataclass(frozen=True)
class Sass(Content):
    source_path: Path

    def render(self, path: SitePath):
        if self.source_path.is_dir():
            css_at_target = construct_relative_css_path(self.source_path, target=path)
            [_render(p, css_at_target(p)) for p in paths(f'{self.source_path}/**/*.sass')]
            [_render(p, css_at_target(p)) for p in paths(f'{self.source_path}/**/*.scss')]
        else:
            _render(self.source_path, path)


def construct_relative_css_path(source: Path, *, target: SitePath) -> Callable[[Path], SitePath]:
    start = len(source.parts)

    def remap(path: Path) -> SitePath:
        relative_parts = path.parts[start:]
        return target.site.path(Path(*target.parts, *relative_parts)).with_suffix('.css')

    return remap


def _render(source: Path, target: SitePath):
    sourcemap_path = target.with_name(target.name + '.map')
    result, sourcemap = compile(
        filename=str(source),
        source_map_filename=str(source.parent / sourcemap_path.name),
        source_map_root=str(source.parent),
        source_map_contents=True,
        output_style='compact',
    )
    target.parent.mkdir()
    with target.open('w') as css_file, sourcemap_path.open('w') as sourcemap_file:
        css_file.write(result)
        sourcemap_file.write(sourcemap)


def sass(location: str) -> Sass:
    path = Path(location)
    if not path.exists():
        raise FileNotFoundError(f'Sass file not found: {location}')
    return Sass(path)
