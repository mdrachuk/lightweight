import os
from contextlib import contextmanager
from glob import glob
from pathlib import Path
from typing import Union, List


def paths(pattern: Union[str, Path]) -> List[Path]:
    """A list of paths matching the provided [glob](https://en.wikipedia.org/wiki/Glob_(programming)) pattern.

    @example
    ```python
    >>> print(paths('lightweight/**/__init__.py'))
    [PosixPath('lightweight/__init__.py'), PosixPath('lightweight/content/__init__.py')]
    >>> print(paths('lightweight/*.typed'))
    [PosixPath('lightweight/py.typed')]
    ```
    """
    if isinstance(pattern, Path):
        return [pattern]
    return [Path(p) for p in glob(pattern, recursive=True)]


@contextmanager
def directory(location: Union[str, Path]):
    """Execute the following statements with provided location as "cwd" (current working directory).

    @example
    ```
    from pathlib import Path

    project_location = Path(__file__).absolute().parent
    with directory(project_location):
        site.include('index.html')
    ```
    """
    cwd = os.getcwd()
    os.chdir(str(location))
    yield
    os.chdir(cwd)
