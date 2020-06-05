from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Tuple, Union

from .path import GenPath

if TYPE_CHECKING:
    from ..site import Site
    from .task import GenTask


class GenContext:
    """A generation context.
    Contains the data useful during the generation: the site and the list of tasks to be executed in the process.

    The context is created by a [Site] upon starting generation
    and provided to the [`Content.write(path, ctx)`][lightweight.content.Content.write] method as a second parameter.
    """
    site: Site
    out: Path
    tasks: Tuple[GenTask, ...]
    generated: datetime  # UTC datetime of generation
    version: str

    def __init__(self, out: Path, site: Site):
        self.out = out
        self.site = site
        self.generated = datetime.utcnow()
        import lightweight
        self.version = lightweight.__version__

    def path(self, p: Union[Path, str]) -> GenPath:
        """Create a new [GenPath] in this generation context from a regular path."""
        return GenPath(Path(p), self.out, lambda location: self.site / location)
