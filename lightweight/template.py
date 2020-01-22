from collections import defaultdict
from os import PathLike, getcwd
from pathlib import Path
from typing import Union, cast, Dict

from jinja2 import Environment, FileSystemLoader, Template, StrictUndefined
from jinja2.utils import LRUCache


class DynamicCwd(PathLike):
    """A path which always points to the current directory."""

    def __fspath__(self):
        return getcwd()


#
# This bit may look a bit dodgy.
# The thing is, for an ability to have isolated subsites, but still use the simple approach with a global Jinja
# environment the environment is set to load templates relative to current working directory.
#
cwd_loader = FileSystemLoader([cast(str, DynamicCwd())], followlinks=True)
jinja_env = Environment(
    loader=cwd_loader,
    cache_size=0,
    lstrip_blocks=True,
    trim_blocks=True,
    undefined=StrictUndefined,
)


class LruCachePerCwd:
    """A proxy for Jinja native LRU cache, supplying cache specific to current working directory."""
    by_cwd: Dict[str, LRUCache]

    def __init__(self, capacity: int):
        self.by_cwd = defaultdict(lambda: LRUCache(capacity))

    def instance(self):
        return self.by_cwd[getcwd()]

    def __getstate__(self, *args, **kwargs):
        return self.instance().__getstate__(*args, **kwargs)

    def __setstate__(self, *args, **kwargs):
        return self.instance().__setstate__(*args, **kwargs)

    def __getnewargs__(self, *args, **kwargs):
        return self.instance().__getnewargs__(*args, **kwargs)

    def copy(self, *args, **kwargs):
        return self.instance().copy(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.instance().get(*args, **kwargs)

    def setdefault(self, *args, **kwargs):
        return self.instance().setdefault(*args, **kwargs)

    def clear(self, *args, **kwargs):
        return self.instance().clear(*args, **kwargs)

    def __contains__(self, *args, **kwargs):
        return self.instance().__contains__(*args, **kwargs)

    def __len__(self, *args, **kwargs):
        return self.instance().__len__(*args, **kwargs)

    def __repr__(self, *args, **kwargs):
        return self.instance().__repr__(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        return self.instance().__getitem__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return self.instance().__setitem__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        return self.instance().__delitem__(*args, **kwargs)

    def items(self, *args, **kwargs):
        return self.instance().items(*args, **kwargs)

    def iteritems(self, *args, **kwargs):
        return self.instance().iteritems(*args, **kwargs)

    def values(self, *args, **kwargs):
        return self.instance().values(*args, **kwargs)

    def itervalue(self, *args, **kwargs):
        return self.instance().itervalue(*args, **kwargs)

    def keys(self, *args, **kwargs):
        return self.instance().keys(*args, **kwargs)

    def iterkeys(self, *args, **kwargs):
        return self.instance().iterkeys(*args, **kwargs)

    def __reversed__(self, *args, **kwargs):
        return self.instance().__reversed__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self.instance().__iter__(*args, **kwargs)

    def __copy__(self, *args, **kwargs):
        return self.instance().__copy__(*args, **kwargs)


jinja_env.cache = LruCachePerCwd(250)


def template(location: Union[str, Path]) -> Template:
    """A shorthand for loading a Jinja2 template from the current working directory."""
    return jinja_env.get_template(str(location))
