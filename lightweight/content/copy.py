from __future__ import annotations

from dataclasses import dataclass
from distutils.dir_util import copy_tree
from pathlib import Path
from shutil import copy
from typing import TYPE_CHECKING

from .content import Content

if TYPE_CHECKING:
    from lightweight.site import SitePath


@dataclass(frozen=True)
class DirectoryCopy(Content):
    source: Path

    def render(self, path: SitePath):
        copy_tree(str(self.source), str(path.absolute()))


@dataclass(frozen=True)
class FileCopy(Content):
    source: Path

    def render(self, path: SitePath):
        path.parent.mkdir(parents=True, exist_ok=True)
        copy(str(self.source), str(path.absolute()))
