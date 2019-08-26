from pathlib import Path
from shutil import rmtree
from typing import overload, Union, Dict

from lightweight.content import Content, FileCopy, DirectoryCopy
from lightweight.errors import NoSourcePath
from lightweight.files import paths


class Site:
    content: Dict[Path, Content]

    def __init__(self, out: Union[str, Path] = 'out'):
        self.out = Path(out)
        self.content = {}

    @overload
    def include(self, pattern: str):
        """Include a file or directory."""
        ...

    @overload
    def include(self, path: Union[str, Path], content: Content):
        """Create a file at path with content."""
        ...

    @overload
    def include(self, path: Content):
        ...

    def include(self, arg: Union[str, Path, Content], content: Content = None):
        if isinstance(arg, Content):
            source_path = getattr(arg, 'source_path', None)
            if source_path is None:
                raise NoSourcePath()
            content, arg = arg, source_path

        if content is None:
            pattern = arg
            contents = {path: _file_or_dir(path) for path in paths(pattern)}
            if not len(contents):
                raise FileNotFoundError()
            self.content.update(contents)
        else:
            path = Path(arg)
            self.content[path] = content

    def render(self):
        if self.out.exists():
            rmtree(self.out)
        self.out.mkdir()
        [content.render(path, self) for path, content in self.content.items()]


def _file_or_dir(path: Path):
    return FileCopy() if path.is_file() else DirectoryCopy()
