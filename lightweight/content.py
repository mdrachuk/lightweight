from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from shutil import copytree, copy
from typing import Optional, TYPE_CHECKING, Union, Any, Dict

from jinja2 import Template, Environment, FileSystemLoader

from lightweight.files import create_file, extension, strip_extension
from lightweight.lw_markdown import LwMarkdown

if TYPE_CHECKING:
    from lightweight.site import Site

jinja_templates = Environment(loader=FileSystemLoader('templates', followlinks=True))
jinja_cwd = Environment(loader=FileSystemLoader('./.', followlinks=True))


def template(name: Union[str, Path]) -> Template:
    """A shorthand for loading a Jinja2 template from `templates` directory."""
    return jinja_templates.get_template(str(name))


class Content(ABC):
    path: Path
    site: Site

    @abstractmethod
    def render(self, path: Path, site: Site):
        """Render..."""


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


class FileName(str):

    @property
    def name(self):
        return strip_extension(self)

    @property
    def extension(self):
        return extension(self)


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


@dataclass
class JinjaSource(Content):
    file: FileName
    source_path: Optional[Path]
    params: Dict[str, Any]
    template: Template

    def render(self, path: Path, site: Site):
        render_to_file(self.template, path, site, source=self, **self.params)


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


def render_to_file(template: Template, path: Path, site: Site, **kwargs) -> None:
    out_path = site.out / path
    out_content = template.render(site=site, **kwargs)
    create_file(out_path, content=out_content)
