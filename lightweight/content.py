from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from shutil import copytree, copy
from typing import Optional, TYPE_CHECKING

import misaka  # type: ignore # missing type annotations
from jinja2 import Template

from lightweight.files import strip_extension

if TYPE_CHECKING:
    from lightweight.site import Site


class Content(ABC):
    path: Path
    site: Site

    @abstractmethod
    def render(self):
        pass

    def register(self, path: Path, site: Site):
        self.path = path
        self.site = site
        return self


@dataclass
class DirectoryCopy(Content):

    def render(self):
        target = self.site.out / self.path
        copytree(str(self.path), str(target))


@dataclass
class FileCopy(Content):

    def render(self):
        target = self.site.out / self.path
        copy(str(self.path), str(target))


@dataclass
class Markdown(Content):
    file_name: str  # name of markdown file without extension
    markdown: str  # the contents of a file

    template: Template

    @property
    def title(self) -> Optional[str]:
        # TODO:mdrachuk:2019-08-19: extract title from YAML Front Matter
        # TODO:mdrachuk:2019-08-19: extract title from first heading
        return None

    @property
    def created(self) -> Optional[date]:
        return None

    @property
    def updated(self) -> Optional[date]:
        return None

    @property
    def html(self):
        return misaka.html(self.markdown)

    @property
    def toc(self):
        # TODO:mdrachuk:2019-08-19: extract Markdown table of contents
        return None

    def render(self):
        self.template.render(site=self.site, markdown=self)


def markdown(path: str, rendered_by: Template):
    path_ = Path(path)

    name = strip_extension(path_.name)
    with path_.open() as f:
        content = f.read()
    return Markdown(
        file_name=name,
        markdown=content,
        template=rendered_by
    )
