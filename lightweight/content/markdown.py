from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional, Union, TYPE_CHECKING, Type

import mistune
from jinja2 import Template

from ..files import FileName
from .content import Content
from .lwmd import LwRenderer

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
        renderer.reset()
        html = mistune.Markdown(renderer).render(self.source)
        toc_html = renderer.render_toc(level=3)
        html, md_title = extract_title(html, strip_from_html=strip_title)
        return RenderedMarkdown(
            html=html,
            toc_html=toc_html,
            # TODO:mdrachuk:2019-08-19: extract title from YAML Front Matter
            title=self.title or md_title,
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


def extract_title(html: str, *, strip_from_html: bool) -> Tupler[str, Optional[str]]:
    heading_regex = re.compile(r'\A<h1.+>(?P<title>.+)</h1>')
    match = heading_regex.match(html)
    if not match:
        return html, None
    title = match.group('title')
    if strip_from_html:
        html = heading_regex.sub('', html, count=1)
    return html, title


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
    if not created and updated:
        created = updated
        updated = updated
    elif created and not updated:
        created = created
        updated = created
    elif not created and not updated:
        created = datetime.fromtimestamp(os.path.getctime(str(path)), tz=timezone.utc)
        updated = datetime.fromtimestamp(os.path.getmtime(str(path)), tz=timezone.utc)
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
