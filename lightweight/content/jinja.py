from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Union, TYPE_CHECKING

from jinja2 import Template

from .content import Content
from ..template import template

if TYPE_CHECKING:
    from lightweight import GenPath, GenContext


@dataclass(frozen=True)
class JinjaPage(Content):
    template: Template
    path: Path
    params: Dict[str, Any]

    def write(self, path: GenPath, ctx: GenContext):
        path.create(self.template.render(
            site=ctx.site,
            ctx=ctx,
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
        params=params,
    )
