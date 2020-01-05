from __future__ import annotations

from dataclasses import dataclass
from distutils.dir_util import copy_tree
from pathlib import Path
from shutil import copy
from typing import TYPE_CHECKING, Union

from .content import Content

if TYPE_CHECKING:
    from lightweight import GenPath, GenContext


@dataclass(frozen=True)
class DirectoryCopy(Content):
    source: Union[Path, str]

    def write(self, path: GenPath, ctx: GenContext):
        path.parent.mkdir()
        copy_tree(str(self.source), str(path.absolute()))


@dataclass(frozen=True)
class FileCopy(Content):
    source: Union[Path, str]

    def write(self, path: GenPath, ctx: GenContext):
        path.parent.mkdir()
        copy(str(self.source), str(path.absolute()))
