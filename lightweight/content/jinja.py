from __future__ import annotations

from dataclasses import dataclass
from os import getcwd
from pathlib import Path
from typing import Dict, Any, Union, TYPE_CHECKING

from jinja2 import Template

from .content import Content
from ..files import directory
from ..template import template

if TYPE_CHECKING:
    from lightweight import RenderPath


@dataclass(frozen=True)
class JinjaPage(Content):
    template: Template
    path: Path
    cwd: str
    params: Dict[str, Any]

    def write(self, path: RenderPath):
        with directory(self.cwd):
            path.create(self.template.render(
                site=path.ctx.site,
                ctx=path.ctx,
                source=self,
                **self.params
            ))


def jinja(template_path: Union[str, Path], **params) -> JinjaPage:
    """Renders the page at path with provided parameters.

    Templates are resolved from current directory (NOT `./templates/`)."""
    path = Path(template_path)
    return JinjaPage(
        template=template(path),
        path=path,
        cwd=getcwd(),
        params=params,
    )
