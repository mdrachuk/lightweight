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
    from lightweight import SitePath, Site


@dataclass(frozen=True)
class MarkdownPage(Content):
    filename: FileName  # name of markdown file
    source_path: Path
    source: str  # the contents of a file
    template: Template

    title: Optional[str] = None
    summary: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

    def render(self, site: Site):
        html, toc_html = LwMarkdown().render(self.source)
        return RenderedMarkdown(
            html=html,
            toc_html=toc_html,
            # TODO:mdrachuk:2019-08-19: extract title from YAML Front Matter
            # TODO:mdrachuk:2019-08-19: extract title from first heading
            title=self.title,
            summary=self.summary,
            created=self.created,
            updated=self.updated,
        )

    def write(self, path: SitePath):
        path.create(self.template.render(
            site=path.site,
            source=self,
            markdown=self.render(path.site)
        ))


def markdown(md_path: Union[str, Path], template: Template, **fields) -> MarkdownPage:
    path = Path(md_path)
    with path.open() as f:
        source = f.read()
    return MarkdownPage(
        filename=FileName(path.name),
        source_path=path,
        source=source,
        template=template,
        **fields
    )


@dataclass(frozen=True)
class RenderedMarkdown:
    html: str
    toc_html: str

    title: Optional[str]
    summary: Optional[str]
    updated: Optional[date]
    created: Optional[date]
