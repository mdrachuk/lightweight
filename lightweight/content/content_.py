from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lightweight import GenPath, GenContext


class Content(ABC):
    """An abstract content that can be included by a [Site][..site.Site]."""

    @abstractmethod
    def write(self, path: GenPath, ctx: GenContext):
        """Write the content to the file at path."""
