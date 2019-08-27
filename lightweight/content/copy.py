from __future__ import annotations

from dataclasses import dataclass
from distutils.dir_util import copy_tree
from pathlib import Path
from shutil import copy
from typing import TYPE_CHECKING

from .content import Content

if TYPE_CHECKING:
    from lightweight import Site


@dataclass
class DirectoryCopy(Content):

    def render(self, path: Path, site: Site):
        target = site.out / path
        copy_tree(str(path), str(target))


@dataclass
class FileCopy(Content):

    def render(self, path: Path, site: Site):
        target = site.out / path
        target.parent.mkdir(parents=True, exist_ok=True)
        copy(str(path), str(target))
