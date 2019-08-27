from pathlib import Path
from typing import TYPE_CHECKING

from .content import Content

if TYPE_CHECKING:
    from lightweight import Site


class Sass(Content):
    def render(self, path: Path, site: Site) -> None:
        pass


def sass(path: str) -> Sass:
    return Sass()
