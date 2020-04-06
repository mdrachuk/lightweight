from __future__ import annotations

import os
from collections import defaultdict
from dataclasses import replace, dataclass
from pathlib import Path
from typing import List, Dict

from lightweight import Content, GenContext
from lightweight.generation import GenTask


class Includes:
    ics: List[IncludedContent]
    by_cwd: Dict[str, List[IncludedContent]]
    by_location: Dict[str, IncludedContent]

    def __init__(self):
        self.ics = []
        self.by_cwd = defaultdict(list)
        self.by_location = {}

    def add(self, ic: IncludedContent):
        self.ics.append(ic)
        self.by_cwd[ic.cwd].append(ic)
        self.by_location[ic.location] = ic

    def __contains__(self, location: str) -> bool:
        return location in self.by_location

    def __iter__(self):
        return iter(self.ics)

    def at_path(self, target: Path) -> Includes:
        target = Path(target)
        cc = Includes()
        for ic in self.ics:
            if all(actual == expected for actual, expected in zip(ic.path.parts, target.parts)):
                new_loc = _clip_path_parts(len(target.parts), ic.path)
                new_ic = replace(ic, location=new_loc)
                cc.add(new_ic)
        return cc


def _clip_path_parts(number: int, path: Path) -> str:
    return os.path.join(*path.parts[number:])


@dataclass(frozen=True)
class IncludedContent:
    """The [content][Content] included by a [Site].

    Contains the site’s location and `cwd` (current working directory) of the content.

    Location is a string with an output path relative to generation out directory.
    It does not include a leading forward slash.

    `cwd` is important for proper subsite generation.
    """
    location: str
    content: Content
    cwd: str

    @property
    def path(self):
        return Path(self.location)

    def make_tasks(self, ctx: GenContext) -> List[GenTask]:
        return [GenTask(ctx.path(self.location), ctx, self.content, self.cwd)]
