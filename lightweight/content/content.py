from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Template

from lightweight.files import create_file

if TYPE_CHECKING:
    from lightweight import Site


class Content(ABC):
    path: Path
    site: Site

    @abstractmethod
    def render(self, path: Path, site: Site):
        """Render..."""


def render_to_file(template: Template, path: Path, site: Site, **kwargs) -> None:
    out_path = site.out / path
    out_content = template.render(site=site, **kwargs)
    create_file(out_path, content=out_content)
