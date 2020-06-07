"""Lightweight [Markdown][1] [Content].

Usage:
```
from lightweight import markdown, template

...

site.add('hello.html', markdown('posts/hello.md', template('templates/post.html')))
```

[1]: https://daringfireball.net/projects/markdown/
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union, TYPE_CHECKING, Type, Dict, Any

import frontmatter  # type: ignore
from jinja2 import Template
from mistune import Markdown  # type: ignore

from .content_abc import Content
from .jinja_page import _eval_if_lazy
from .lwmd import LwRenderer, TableOfContents

if TYPE_CHECKING:
    from lightweight import GenPath, GenContext


@dataclass(frozen=True)
class MarkdownPage(Content):
    """Content generated from rendering a markdown file to a Jinja template."""

    template: Template  # Jinja2 template
    source_path: Path  # path to the markdown file
    text: str = field(repr=False)  # the contents of a markdown file

    renderer: Type[LwRenderer] = field(repr=False)

    title: Optional[str]
    summary: Optional[str] = field(repr=False)
    created: Optional[datetime] = field(repr=False)
    updated: Optional[datetime] = field(repr=False)

    front_matter: Dict[str, Any] = field(repr=False)
    props: Dict[str, Any] = field(repr=False)

    def write(self, path: GenPath, ctx: GenContext):
        """Writes a rendered Jinja template with rendered Markdown, parameters from front-matter and code
        to the file provided path."""
        # TODO:mdrachuk:06.01.2020: warn if site, ctx, source are in props or front matter!
        path.create(self.template.render(
            site=ctx.site,
            ctx=ctx,
            content=self,
            markdown=self.render(ctx),
            **self.front_matter,
            **self._evaluated_props(ctx),
        ))

    def render(self, ctx: GenContext) -> RenderedMarkdown:
        """Render Markdown to html, extracting the ToC."""
        link_mapping = self._map_links(ctx)
        renderer = self.renderer(link_mapping)
        html = Markdown(renderer).render(self.text)
        toc = renderer.table_of_contents(level=3)
        preview_html = self._extract_preview(html)
        return RenderedMarkdown(
            html=html,
            preview_html=preview_html,
            toc=toc
        )

    @staticmethod
    def _map_links(ctx: GenContext):
        """Map links allowing in Markdown to reference other Markdown pages by their ".md" files
        and using relative paths for other files."""
        link_mapping = {str(task.path): task.path.url for task in ctx.tasks}
        link_mapping.update({
            str(task.content.source_path): task.path.url
            for task in ctx.tasks
            if isinstance(task.content, MarkdownPage)
        })
        return link_mapping

    @staticmethod
    def _extract_preview(html):
        preview_split = html.split('<!--preview-->', maxsplit=1)
        preview_html = preview_split[0] if len(preview_split) == 2 else None
        return preview_html

    def _evaluated_props(self, ctx) -> Dict[str, Any]:
        return {key: _eval_if_lazy(value, ctx) for key, value in self.props.items()}


def markdown(md_path: Union[str, Path], template: Union[Template], *, renderer=LwRenderer, **kwargs) -> MarkdownPage:
    """Create a markdown page that can be included by a Site.
    Markdown page is compiled from a markdown file at path (*.md) and a [Jinja Template][lightweight.template].

    Provided key-word arguments are passed as props to the template on render.
    Such props can also be lazily evaluated from [GenContext]
    by using the [from_ctx(func) decorator][lightweight.content.jinja_page.from_ctx].
    """
    path = Path(md_path)
    source = path.read_text(encoding='utf-8')
    fm = frontmatter.loads(source)
    title = fm.get('title', None)
    summary = fm.get('summary', None)
    created = fm.get('created', None)
    updated = fm.get('updated', created)
    if created is not None:
        assert isinstance(created, datetime), '"created" is not a valid datetime object'
        created = created.replace(tzinfo=timezone.utc)
    if updated is not None:
        assert isinstance(updated, datetime), '"updated" is not a valid datetime object'
        updated = updated.replace(tzinfo=timezone.utc)
    return MarkdownPage(
        template=template,
        text=fm.content,
        source_path=path,

        renderer=renderer,

        title=title,
        summary=summary,
        created=created,
        updated=updated,

        front_matter=fm,
        props=dict(kwargs),
    )


@dataclass(frozen=True)
class RenderedMarkdown:
    """The result of parsing and rendering Markdown."""
    html: str
    preview_html: str
    toc: TableOfContents
