from os import PathLike, getcwd
from pathlib import Path
from typing import Union

from jinja2 import Environment, FileSystemLoader, Template


class DynamicCwd(PathLike):
    def __fspath__(self):
        return getcwd()


cwd_loader = FileSystemLoader([DynamicCwd()], followlinks=True)
jinja = Environment(loader=cwd_loader, cache_size=0)


def template(name: Union[str, Path], base_dir: Union[str, Path] = 'templates') -> Template:
    """A shorthand for loading a Jinja2 template from `templates` directory."""
    location = str(Path(base_dir) / Path(name))
    return jinja.get_template(location)
