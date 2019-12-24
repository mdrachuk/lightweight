from os import PathLike, getcwd
from pathlib import Path
from typing import Union

from jinja2 import Environment, FileSystemLoader, Template


class DynamicCwd(PathLike):
    def __fspath__(self):
        return getcwd()


cwd_loader = FileSystemLoader([DynamicCwd()], followlinks=True)
jinja = Environment(loader=cwd_loader, cache_size=0)


def template(location: Union[str, Path]) -> Template:
    """A shorthand for loading a Jinja2 template from `templates` directory."""
    return jinja.get_template(str(location))
