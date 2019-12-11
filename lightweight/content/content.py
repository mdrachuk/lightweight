from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lightweight import RenderPath

# Type aliases for clear type definitions
Url = str
Email = str


class Content(ABC):

    @abstractmethod
    def write(self, path: RenderPath):
        """Write..."""


class Entry(ABC):
    """A definition of an Entry interface. Properties defined by Entry can be used by other modules, e.g. feed."""

    url: Url
    title: str
    content: str
    author_name: str
    author_email: Email
    created: datetime
    updated: datetime
