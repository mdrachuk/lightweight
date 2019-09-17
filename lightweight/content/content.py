from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Union

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
    """A definition of an Entry interface. Properties defined by Entry can be used by other modules, e.g. feed."""

    url: Url
    title: str
    content: str
    author_name: str
    author_email: Email
    created: datetime
    updated: datetime


class ByteContent(Content, bytes):
    """Bytes that can be redered to path.

        :Example:

        >>> binary_content = ByteContent(b'1234')
        >>> binary_content.render(site.path('out/digits.bin'))
    """

    def render(self, path: SitePath):
        path.create(self)

    def __repr__(self):
        return f'<{self.__class__.__name__} {truncate(self)}>'


def truncate(string: Union[str, bytes], size=16) -> str:
    return f'{string[:size]}..' if len(string) > size else str(string)
