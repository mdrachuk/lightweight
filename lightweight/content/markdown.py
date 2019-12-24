from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from os import getcwd
from pathlib import Path
from typing import Optional, Union, TYPE_CHECKING, Type, Dict, Any

import frontmatter  # type: ignore
from jinja2 import Template
from mistune import Markdown  # type: ignore

from .content import Content
from .lwmd import LwRenderer, TableOfContents
from ..files import directory

if TYPE_CHECKING:
    from lightweight import RenderPath, Rendering


@dataclass(frozen=True)
class MarkdownPage(Content):
    template: Template  # Jinja2 template
    source: str  # the contents of a markdown file
    path: Path  # path to the markdown file
    cwd: str

    renderer: Type[LwRenderer]

    title: Optional[str]
    summary: Optional[str]
    created: Optional[datetime]
    updated: Optional[datetime]
    order: Optional[Union[int, float]]

    options: Dict[str, Any]

    def render(self, ctx: Rendering):
        link_mapping = self.map_links(ctx)
        renderer = self.renderer(link_mapping)
        html = Markdown(renderer).render(self.source)
        toc = renderer.table_of_contents(level=3)
        preview_html = self.extract_preview(html)
        return RenderedMarkdown(
            html=html,
            preview_html=preview_html,
            toc=toc,
            title=self.title,
            summary=self.summary,
            created=self.created,
            updated=self.updated,
            options=self.options,
        )

    @staticmethod
    def map_links(ctx: Rendering):
        md_paths = {
            str(content.path): path.url
            for path, content in ctx.tasks.items()
            if isinstance(content, MarkdownPage)
        }
        locations = {str(p): p.url for p in ctx.tasks}
        link_mapping = dict(**md_paths, **locations)
        return link_mapping

    @staticmethod
    def extract_preview(html):
        preview_split = html.split('<!--preview-->', maxsplit=1)
        preview_html = preview_split[0] if len(preview_split) == 2 else None
        return preview_html

    def write(self, path: RenderPath):
        with directory(self.cwd):
            path.create(self.template.render(
                site=path.ctx.site,
                ctx=path.ctx,
                source=self,
                markdown=self.render(path.ctx)
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
        template=template,
        source=post.content,
        path=path,
        cwd=getcwd(),

        renderer=renderer,

        title=title,
        summary=summary,
        created=created,
        updated=updated,
        order=order,
        options=dict(post),
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
    options: Dict[str, Any]
