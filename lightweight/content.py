from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from shutil import copytree, copy
from typing import Optional, TYPE_CHECKING

from jinja2 import Template

from lightweight.files import strip_extension
from lightweight.lw_markdown import LwMarkdown

if TYPE_CHECKING:
    from lightweight.site import Site


class Content(ABC):
    path: Path
    site: Site

    @abstractmethod
    def render(self, path: Path, site: Site):
        pass


@dataclass
class DirectoryCopy(Content):

    def render(self, path: Path, site: Site):
        target = site.out / path
        copytree(str(path), str(target))


@dataclass
class FileCopy(Content):

    def render(self, path: Path, site: Site):
        target = site.out / path
        target.parent.mkdir(parents=True, exist_ok=True)
        copy(str(path), str(target))


@dataclass
class MarkdownSource(Content):
    file_name: str  # name of markdown file without extension
    content: str  # the contents of a file
    template: Template

    def render(self, path: Path, site: Site):
        html, toc_html = LwMarkdown().render(self.content)
        page = self.template.render(
            site=site,
            markdown=RenderedMarkdown(
                html=html,
                toc_html=toc_html,
                # TODO:mdrachuk:2019-08-19: extract title from YAML Front Matter
                # TODO:mdrachuk:2019-08-19: extract title from first heading
                title=None,
                updated=None,
                created=None,
                file_name=self.file_name,
                source_text=self.content,
            ))
        out = site.out / path
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open('w') as f:
            f.write(page)


@dataclass
class RenderedMarkdown:
    html: str
    toc_html: str
    title: Optional[str]
    updated: Optional[date]
    created: Optional[date]
    file_name: str
    source_text: str


def markdown(path: str, rendered_by: Template):
    path_ = Path(path)

    name = strip_extension(path_.name)
    with path_.open() as f:
        content = f.read()
    return MarkdownSource(
        file_name=name,
        content=content,
        template=rendered_by
    )
