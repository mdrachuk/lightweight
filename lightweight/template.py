from pathlib import Path
from typing import Union

from jinja2 import Environment, FileSystemLoader, Template

jinja_templates = Environment(loader=FileSystemLoader('./.', followlinks=True))


def template(name: Union[str, Path], base_dir: Union[str, Path] = 'templates') -> Template:
    """A shorthand for loading a Jinja2 template from `templates` directory."""
    return jinja_templates.get_template(str(_concat(base_dir, name)))


def _concat(base: Union[str, Path], path: Union[str, Path]):
    base = Path(base)
    path = Path(path)
    if path.is_absolute():
        return path
    else:
        return base / path
