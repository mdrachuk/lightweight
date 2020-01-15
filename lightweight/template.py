from os import PathLike, getcwd
from pathlib import Path
from typing import Union, cast

from jinja2 import Environment, FileSystemLoader, Template


class DynamicCwd(PathLike):
    """This is a path, that upon use always points to the current directory."""

    # TODO:mdrachuk:24.12.2019: implement str interface (mostly, hash should probably raise an error, etc)
    def __fspath__(self):
        return getcwd()


#
# This bit may look a bit dodgy.
# The thing is, for an ability to have isolated subsites, but still use the simple approach with a global Jinja
# environment the environment is set to load templates relative to current working directory.
#
cwd_loader = FileSystemLoader([cast(str, DynamicCwd())], followlinks=True)
jinja_env = Environment(loader=cwd_loader, cache_size=0, lstrip_blocks=True, trim_blocks=True)


def template(location: Union[str, Path]) -> Template:
    """A shorthand for loading a Jinja2 template from the current working directory."""
    return jinja_env.get_template(str(location))
