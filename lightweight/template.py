from pathlib import Path
from typing import Union

from jinja2 import Environment, FileSystemLoader, Template

jinja = Environment(loader=FileSystemLoader('./.', followlinks=True))


def template(name: Union[str, Path], base_dir: Union[str, Path] = 'templates') -> Template:
    """A shorthand for loading a Jinja2 template from `templates` directory."""
    location = str(Path(base_dir) / Path(name))
    return jinja.get_template(location)
