from pathlib import Path
from shutil import rmtree
from typing import List, overload, Union

from jinja2 import Environment, FileSystemLoader

from lightweight.content import Content, FileCopy, DirectoryCopy


class Site:
    content: List[Content]

    def __init__(self, out: Union[str, Path] = 'out'):
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.out = Path(out)
        self.content = []

    @overload
    def include(self, path_: str):
        """Include a file or directory."""
        ...

    @overload
    def include(self, path_: str, content: Content):
        """Create a file at path with content."""
        ...

    def include(self, path_: str, content: Content = None):
        path = Path(path_)
        if content is None:
            if not path.exists():
                raise FileNotFoundError()
            content = FileCopy() if path.is_file() else DirectoryCopy()
        content.register(path, self)
        self.content.append(content)

    def template(self, name):
        return self.env.get_template(name)

    def render(self):
        if self.out.exists():
            rmtree(self.out)
        self.out.mkdir()
        [content.render() for content in self.content]
