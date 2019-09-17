from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lightweight import Site, SitePath

# Type aliases for clear type definitions
Url = str
Email = str


class Content(ABC):
    path: Path
    site: Site

    @abstractmethod
    def render(self, path: SitePath):
        """Render..."""


class Entry(ABC):
    link: Url
    title: str
    content: str
    author_name: str
    author_email: Email
    created: datetime
    updated: datetime
