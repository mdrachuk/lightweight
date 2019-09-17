from __future__ import annotations

import datetime
from abc import ABC
from pathlib import Path
from typing import Mapping, Dict, TYPE_CHECKING, Collection, Iterator, Any, Tuple

if TYPE_CHECKING:
    from lightweight import Content

# Type aliases for clear type definitions
Url = str
LanguageCode = str
Email = str


class ContentCollection:
    def __init__(self, content: Mapping[Path, Content]):
        self.content = dict(content)

    def __getitem__(self, path_part: str) -> ContentAtPath:
        content = self.content_at_path(path_part)
        if not content:
            raise KeyError(f'There is no content at path "{path_part}"')
        return ContentAtPath(self, Path(path_part), content)

    def __iter__(self):
        return iter(self.content.values())

    def content_at_path(self, path_part):
        return {
            path: content
            for path, content in self.content.items()
            if path.parts[0] == path_part
        }


class EntriesCollection(ABC):
    take_after_fields = frozenset({
        'url', 'icon_url', 'title', 'description', 'author_name', 'author_email', 'language', 'copyright', 'updated'
    })
    url: Url
    icon_url: Url
    title: str
    description: str
    author_name: str
    author_email: Email
    language: LanguageCode
    copyright: str  # Full notice.
    updated: datetime

    def take_after(self, source: Any = None, **custom: Mapping[str, Any]) -> None:
        if source:
            for field, value in self.field_value(source, self.take_after_fields - custom.keys()):
                setattr(self, field, value)
        for field, value in custom.items():
            setattr(self, field, value)

    @classmethod
    def field_value(cls, collection: EntriesCollection, fields: Collection[str]) -> Iterator[Tuple[str, Any]]:
        return (
            (field, getattr(collection, field))
            for field in fields
            if hasattr(collection, field)
        )


class ContentAtPath(EntriesCollection, ContentCollection):

    def __init__(self, root: ContentCollection, path: Path, content: Dict[Path, Content]):
        super().__init__(content)
        self.root = root
        self.relative_path = path
        self.base_size = len(self.relative_path.parts)

        self.take_after(root)
        self.url = str(path)  # TODO:mdrachuk:9/11/19: switch for an absolute url
        self.description = f'{self.title} | {self.relative_path}'

    def __getitem__(self, path_part: str):
        return ContentAtPath(self.root, self.relative_path / Path(path_part), {
            path: content
            for path, content in self.content.items()
            if len(path.parts) > self.base_size and path.parts[self.base_size] == path_part
        })
