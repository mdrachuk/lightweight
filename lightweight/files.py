from glob import iglob
from pathlib import Path
from typing import Iterator, Optional, Union


def paths(glob_path: Union[str, Path]) -> Iterator[Path]:
    """An iterator of paths matching the provided `glob`_ pattern.

    _glob: https://en.wikipedia.org/wiki/Glob_(programming)"""
    if isinstance(glob_path, Path):
        return iter([glob_path])
    return map(Path, iglob(glob_path, recursive=True))


def strip_extension(file_name: str) -> str:
    split = file_name.rsplit('.', 1)
    if not len(split[0]) or not len(split[1]):
        return file_name
    return split[0]


def extension(file_name: str) -> Optional[str]:
    split = file_name.rsplit('.', 1)
    if len(split) < 2 or not len(split[0]) or not len(split[1]):
        return None
    return split[1]


class FileName(str):

    @property
    def stem(self):
        return strip_extension(self)

    @property
    def extension(self):
        return extension(self)
