from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Template

from lightweight.files import create_file

if TYPE_CHECKING:
    from lightweight import Site
    from lightweight.site import SitePath


class Content(ABC):
    path: Path
    site: Site

    @abstractmethod
    def render(self, path: SitePath):
        """Render..."""


def render_to_file(template: Template, path: SitePath, **kwargs) -> None:
    out_content = template.render(site=path.site, **kwargs)
    create_file(path.real_path, content=out_content)
