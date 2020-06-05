"""This module configures a Jinja environment to use with the app ([`jinja_env`]).
This environment is configured to locate templates and resolve their inner references according to
the current working directory (`cwd`).

Also a [strict undefined][1] is enabled.
This means that any operations with an undefined Jinja template parameter will result in an error.
This is a safer approach in contrast to Jinja defaults.

[`template`] is a shortcut for loading templates using this environment.

[1]: https://jinja.palletsprojects.com/en/2.11.x/api/#undefined-types
"""
__all__ = ['template', 'jinja_env']

from collections import defaultdict
from os import getcwd, path, walk
from pathlib import Path
from typing import Union, Dict

from jinja2 import Environment, Template, StrictUndefined, BaseLoader, TemplateNotFound
from jinja2.loaders import split_template_path
from jinja2.utils import LRUCache, open_if_exists


class CwdLoader(BaseLoader):

    def get_source(self, environment, template):
        pieces = split_template_path(template)
        searchpath = getcwd()
        filename = path.join(searchpath, *pieces)
        f = open_if_exists(filename)
        if f is None:
            raise TemplateNotFound(template)
        try:
            contents = f.read().decode('utf-8')
        finally:
            f.close()

        mtime = path.getmtime(filename)

        def uptodate():
            try:
                return path.getmtime(filename) == mtime
            except OSError:
                return False

        return contents, filename, uptodate

    def list_templates(self):
        found = set()
        searchpath = getcwd()
        walk_dir = walk(searchpath, followlinks=False)
        for dirpath, _, filenames in walk_dir:
            for filename in filenames:
                template = (
                    path.join(dirpath, filename)[len(searchpath):]
                        .strip(path.sep)
                        .replace(path.sep, "/")
                )
                if template[:2] == "./":
                    template = template[2:]
                if template not in found:
                    found.add(template)
        return sorted(found)


jinja_env = Environment(
    loader=CwdLoader(),
    cache_size=0,  # does not affect anything, cache set below
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
