from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from shutil import copy as shcopy, copytree
from typing import TYPE_CHECKING, Union

from .content import Content
from ..generation import schedule

if TYPE_CHECKING:
    from lightweight import GenPath, GenContext


@dataclass(frozen=True)
class DirectoryCopy(Content):
    """Site content which is a copy of a directory from the path provided as source."""
    source: Union[Path, str]

    async def write(self, path: GenPath, ctx: GenContext):
        await path.parent.a_mkdir()
        await schedule(copytree, str(self.source), str(path.absolute()))


@dataclass(frozen=True)
class FileCopy(Content):
    """Site content which is a copy fof a file from the path provided as source."""
    source: Union[Path, str]

    async def write(self, path: GenPath, ctx: GenContext):
        await path.parent.a_mkdir()
        await schedule(shcopy, str(self.source), str(path.absolute()))


def copy(path: Union[str, Path]):
    """Copy file or directory at path, ensuring their existence."""
    path = Path(path)
    return FileCopy(path) if path.is_file() else DirectoryCopy(path)
