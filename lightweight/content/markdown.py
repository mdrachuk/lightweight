from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional, Union, TYPE_CHECKING

from jinja2 import Template

from lightweight.files import FileName
from .content import Content, render_to_file
from .lwmd import LwMarkdown

if TYPE_CHECKING:
    from lightweight import Site


@dataclass
class MarkdownSource(Content):
    file: FileName  # name of markdown file
    source_path: Optional[Path]
    content: str  # the contents of a file
    template: Template

    def render(self, path: Path, site: Site):
        html, toc_html = LwMarkdown().render(self.content)
        render_to_file(
            self.template, path, site,
            markdown=RenderedMarkdown(
                html=html,
                toc_html=toc_html,
                # TODO:mdrachuk:2019-08-19: extract title from YAML Front Matter
                # TODO:mdrachuk:2019-08-19: extract title from first heading
                title=None,
                updated=None,
                created=None
            ),
            source=self,
        )


def markdown(md_path: Union[str, Path], template: Template) -> MarkdownSource:
    path = Path(md_path)
    with path.open() as f:
        content = f.read()
    return MarkdownSource(
        file=FileName(path.name),
        source_path=path,
        content=content,
        template=template
    )


@dataclass
class RenderedMarkdown:
    html: str
    toc_html: str
    title: Optional[str]
    updated: Optional[date]
    created: Optional[date]