from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, Union, TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader, Template

from lightweight.files import FileName
from .content import Content

if TYPE_CHECKING:
    from lightweight import SitePath

jinja_cwd = Environment(loader=FileSystemLoader('./.', followlinks=True))


@dataclass
class JinjaSource(Content):
    file: FileName
    source_path: Optional[Path]
    params: Dict[str, Any]
    template: Template

    def render(self, path: SitePath):
        path.create(self.template.render(
            site=path.site, source=self, **self.params
        ))


def render(template_path: Union[str, Path], **params) -> JinjaSource:
    """Renders the page at path with provided parameters.

    Templates are resolved from current directory (NOT `./templates/`)."""
    path = Path(template_path)
    return JinjaSource(
        file=FileName(path.name),
        source_path=path,
        params=params,
        template=jinja_cwd.get_template(str(path))
    )
