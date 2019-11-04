from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional, Union, TYPE_CHECKING, Type

from jinja2 import Template

from lightweight.files import FileName
from .content import Content
from .lwmd import LwMarkdown, LwRenderer

if TYPE_CHECKING:
    from lightweight import SitePath


@dataclass(frozen=True)
class MarkdownPage(Content):
    filename: FileName  # name of markdown file
    source_path: Path
    source: str  # the contents of a file
    template: Template

    renderer: Type[LwRenderer]

    title: Optional[str] = None
    summary: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

    def render(self, path: SitePath, strip_title=False):
        site = path.site
        md_paths = {
            str(content.source_path): path.url
            for path, content in site.items()
            if isinstance(content, MarkdownPage)
        }
        locations = {str(p): p.url for p in site}
        link_mapping = dict(**md_paths, **locations)
        renderer = self.renderer(link_mapping)
        html, toc_html = LwMarkdown(renderer).render(self.source)
        heading_regex = re.compile(r'\A<h1.+>(?P<title>.+)</h1>')
        heading = heading_regex.match(html)
        title = self.title or heading.group('title')
        if strip_title:
            html = heading_regex.sub('', html, count=1)
        return RenderedMarkdown(
            html=html,
            toc_html=toc_html,
            # TODO:mdrachuk:2019-08-19: extract title from YAML Front Matter
            title=title,
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


def markdown(
        md_path: Union[str, Path],
        template: Template,
        renderer=LwRenderer,
        created=None,
        updated=None,
        **fields
) -> MarkdownPage:
    path = Path(md_path)
    with path.open() as f:
        source = f.read()
    created = created or datetime.fromtimestamp(os.path.getctime(str(path)), tz=timezone.utc)
    updated = updated or datetime.fromtimestamp(os.path.getmtime(str(path)), tz=timezone.utc)
    return MarkdownPage(
        filename=FileName(path.name),
        source_path=path,
        source=source,
        template=template,
        renderer=renderer,
        created=created,
        updated=updated,
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
