from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lightweight import Site, SitePath


class Content(ABC):
    path: Path
    site: Site

    @abstractmethod
    def render(self, path: SitePath):
        """Render..."""
