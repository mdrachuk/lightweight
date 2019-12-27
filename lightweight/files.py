import os
from contextlib import contextmanager
from glob import glob
from pathlib import Path
from typing import Union, List


def paths(pattern: Union[str, Path]) -> List[Path]:
    """A list of paths matching the provided [glob](https://en.wikipedia.org/wiki/Glob_(programming)) pattern."""
    if isinstance(pattern, Path):
        return [pattern]
    return [Path(p) for p in glob(pattern, recursive=True)]


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
