import os
from contextlib import contextmanager
from glob import iglob
from pathlib import Path
from typing import Iterator, Union


def paths(glob: Union[str, Path]) -> Iterator[Path]:
    """An iterator of paths matching the provided `glob`_ pattern.

    _glob: https://en.wikipedia.org/wiki/Glob_(programming)"""
    if isinstance(glob, Path):
        return iter([glob])
    return map(Path, iglob(glob, recursive=True))


@contextmanager
def directory(location: str):
    """Execute the following statements with provided location as "cwd" (current working directory).

        :Example:
        from pathlib import Path

        project_location = Path(__file__).absolute().parent
        with directory(project_location):
            site.include('index.html')

    """
    cwd = os.getcwd()
    os.chdir(location)
    yield
    os.chdir(cwd)
