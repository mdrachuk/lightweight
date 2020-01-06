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
    """A file rendered from a Jinja Template."""

    template: Template
    source_path: Path
    params: Dict[str, Any]

    def write(self, path: GenPath, ctx: GenContext):
        path.create(self.render(ctx))

    def render(self, ctx):
        # TODO:mdrachuk:06.01.2020: warn if site, ctx, source are in params!
        return self.template.render(
            site=ctx.site,
            ctx=ctx,
            source=self,
            **self.params
        ))


def jinja(template_path: Union[str, Path], **params) -> JinjaPage:
    """Renders the page at path with provided parameters.

    Templates are resolved from the current directory (cwd).
    """
    path = Path(template_path)
    return JinjaPage(
        template=template(path),
        source_path=path,
        params=params,
    )
