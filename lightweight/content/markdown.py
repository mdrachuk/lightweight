from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Union, TYPE_CHECKING

from jinja2 import Template

from lightweight.files import FileName
from .content import Content
from .lwmd import LwMarkdown

if TYPE_CHECKING:
    from lightweight import SitePath


@dataclass(frozen=True)
class MarkdownSource(Content):
    file: FileName  # name of markdown file
    source_path: Optional[Path]
    content: str  # the contents of a file
    template: Template

    title: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

    def render(self, path: SitePath):
        html, toc_html = LwMarkdown().render(self.content)
        path.create(self.template.render(
            site=path.site,
            source=self,
            markdown=RenderedMarkdown(
                html=html,
                toc_html=toc_html,
                # TODO:mdrachuk:2019-08-19: extract title from YAML Front Matter
                # TODO:mdrachuk:2019-08-19: extract title from first heading
                title=self.title,
                created=self.created,
                updated=self.updated,
            )
        ))


def markdown(md_path: Union[str, Path], template: Template, **fields) -> MarkdownSource:
    path = Path(md_path)
    with path.open() as f:
        content = f.read()
    return MarkdownSource(
        file=FileName(path.name),
        source_path=path,
        content=content,
        template=template,
        **fields
    )


@dataclass(frozen=True)
class RenderedMarkdown:
    html: str
    toc_html: str
    title: Optional[str]
    updated: Optional[date]
    created: Optional[date]
