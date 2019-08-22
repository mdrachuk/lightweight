from pathlib import Path
from shutil import rmtree
from typing import overload, Union, Dict

from jinja2 import Environment, FileSystemLoader

from lightweight.content import Content, FileCopy, DirectoryCopy
from lightweight.files import paths


class Site:
    content: Dict[Path, Content]

    def __init__(self, out: Union[str, Path] = 'out'):
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.out = Path(out)
        self.content = {}

    @overload
    def include(self, path_: str):
        """Include a file or directory."""
        ...

    @overload
    def include(self, path_: str, content: Content):
        """Create a file at path with content."""
        ...

    def include(self, path_: str, content: Content = None):
        if content is None:
            contents = {path: _file_or_dir(path) for path in paths(path_)}
            if not len(contents):
                raise FileNotFoundError()
            self.content.update(contents)
        else:
            path = Path(path_)
            self.content[path] = content

    def template(self, name):
        return self.env.get_template(name)

    def render(self):
        if self.out.exists():
            rmtree(self.out)
        self.out.mkdir()
        [content.render(path, self) for path, content in self.content.items()]


def _file_or_dir(path: Path):
    return FileCopy() if path.is_file() else DirectoryCopy()
