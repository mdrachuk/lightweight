from glob import iglob
from pathlib import Path
from typing import Iterator, Optional, Union


def paths(glob: Union[str, Path]) -> Iterator[Path]:
    """An iterator of paths matching the provided `glob`_ pattern.

    _glob: https://en.wikipedia.org/wiki/Glob_(programming)"""
    if isinstance(glob, Path):
        return iter([glob])
    return map(Path, iglob(glob, recursive=True))

