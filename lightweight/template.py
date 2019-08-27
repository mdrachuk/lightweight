from pathlib import Path
from typing import Union

from jinja2 import Environment, FileSystemLoader, Template

jinja_templates = Environment(loader=FileSystemLoader('templates', followlinks=True))


def template(name: Union[str, Path]) -> Template:
    """A shorthand for loading a Jinja2 template from `templates` directory."""
    return jinja_templates.get_template(str(name))