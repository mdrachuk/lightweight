from pathlib import Path
from typing import Union, Any

from jinja2 import Environment, FileSystemLoader, Template, contextfilter

jinja = Environment(loader=FileSystemLoader('./.', followlinks=True))


@contextfilter
def url(ctx: Any, path: Path) -> str:
    location = str(path.with_suffix('') if path.suffix == '.html' else path)
    return f'{ctx["site"].url}/{location}'


jinja.filters['url'] = url


def template(name: Union[str, Path], base_dir: Union[str, Path] = 'templates') -> Template:
    """A shorthand for loading a Jinja2 template from `templates` directory."""
    return jinja.get_template(str(_concat(base_dir, name)))


def _concat(base: Union[str, Path], path: Union[str, Path]):
    base = Path(base)
    path = Path(path)
    if path.is_absolute():
        return path
    else:
        return base / path
