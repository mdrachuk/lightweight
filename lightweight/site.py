from pathlib import Path
from shutil import rmtree
from typing import overload, Union, Dict, Optional

from lightweight.content import Content, FileCopy, DirectoryCopy
from lightweight.errors import NoSourcePath
from lightweight.files import paths


class Site:
    content: Dict[Path, Content]

    def __init__(self, out: Union[str, Path] = 'out'):
        self.out = Path(out)
        self.content = {}

    @overload
    def include(self, arg: str) -> None:
        """Include a file or directory."""

    @overload
    def include(self, arg: Union[str, Path], content: Content) -> None:
        """Create a file at path with content."""

    @overload
    def include(self, arg: Content) -> None:
        """"""

    def include(self, arg: Union[str, Path, Content], content: Content = None) -> None:
        if isinstance(arg, Content):
            source_path = getattr(arg, 'source_path', None)  # type: Optional[Path]
            if source_path is None:
                raise NoSourcePath()
            arg, content = source_path, arg  # type: ignore

        pattern_or_path = arg  # type: Union[str, Path]
        if content is None:
            contents = {path: _file_or_dir(path) for path in paths(pattern_or_path)}
            if not len(contents):
                raise FileNotFoundError()
            self.content.update(contents)
        else:
            path = Path(pattern_or_path)
            self.content[path] = content

    def render(self):
        if self.out.exists():
            rmtree(self.out)
        self.out.mkdir()
        [content.render(path, self) for path, content in self.content.items()]


def _file_or_dir(path: Path):
    return FileCopy() if path.is_file() else DirectoryCopy()
