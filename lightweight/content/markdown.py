from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional, Union, TYPE_CHECKING, Type, Dict, Any

import frontmatter  # type: ignore
from jinja2 import Template
from mistune import Markdown  # type: ignore

from lightweight.files import FileName
from .content import Content
from .lwmd import LwRenderer, TableOfContents

if TYPE_CHECKING:
    from lightweight import SitePath


@dataclass(frozen=True)
class MarkdownPage(Content):
    filename: FileName  # name of markdown file
    source_path: Path
    source: str  # the contents of a file
    template: Template

    renderer: Type[LwRenderer]

    title: Optional[str]
    summary: Optional[str]
    created: Optional[datetime]
    updated: Optional[datetime]
    order: Optional[Union[int, float]]

    metadata: Dict[str, Any]

    def render(self, path: SitePath):
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
        html = Markdown(renderer).render(self.source)
        toc = renderer.render_toc(level=3)
        preview_split = html.split('<!--preview-->', maxsplit=1)
        preview_html = preview_split[0] if len(preview_split) == 2 else None
        return RenderedMarkdown(
            html=html,
            preview_html=preview_html,
            toc=toc,
            title=self.title,
            summary=self.summary,
            created=self.created,
            updated=self.updated,
        )

    def write(self, path: SitePath):
        path.create(self.template.render(
            site=path.site,
            source=self,
            markdown=self.render(path)
        ))


def markdown(md_path: Union[str, Path], template: Template, *, renderer=LwRenderer) -> MarkdownPage:
    path = Path(md_path)
    with path.open() as f:
        source = f.read()
    post = frontmatter.loads(source)
    title = post.get('title', None)
    summary = post.get('summary', None)
    created = post.get('created', None)
    updated = post.get('updated', created)
    if created is not None:
        assert isinstance(created, datetime), '"created" is not a valid datetime object'
        created = created.replace(tzinfo=timezone.utc)
    if updated is not None:
        assert isinstance(updated, datetime), '"updated" is not a valid datetime object'
        updated = updated.replace(tzinfo=timezone.utc)
    order = post.get('order', None)
    return MarkdownPage(
        filename=FileName(path.name),
        source_path=path,
        source=post.content,
        template=template,

        renderer=renderer,

        title=title,
        summary=summary,
        created=created,
        updated=updated,
        order=order,
        metadata=dict(post),
    )


@dataclass(frozen=True)
class RenderedMarkdown:
    html: str
    preview_html: str
    toc: TableOfContents

    title: Optional[str]
    summary: Optional[str]
    updated: Optional[date]
    created: Optional[date]
