"""Lightweight utilities for working with files."""
import os
from contextlib import contextmanager
from glob import glob
from pathlib import Path
from typing import Union, List


def paths(pattern: Union[str, Path]) -> List[Path]:
    """List paths matching the provided [glob][1] pattern.

    ```python
    >>> print(paths('lightweight/**/__init__.py'))
    [PosixPath('lightweight/__init__.py'), PosixPath('lightweight/content/__init__.py')]

    >>> print(paths('lightweight/*.typed'))
    [PosixPath('lightweight/py.typed')]
    ```

    [1]: https://en.wikipedia.org/wiki/Glob_(programming)
    """
    if isinstance(pattern, Path):
        return [pattern]
    return [Path(p) for p in glob(pattern, recursive=True)]


@contextmanager
def directory(location: Union[str, Path]):
    """Execute following statements using the provided location as "cwd" (current working directory).

    ```python
    from pathlib import Path

    project_location = Path(__file__).absolute().parent

    with directory(project_location):
        site.add('index.html')

    ```
    """
    cwd = os.getcwd()
    os.chdir(str(location))
    yield
    os.chdir(cwd)
