"""
The import like
if TYPE_CHECKING:
    import bla_bla

Only covered after reloading module with TYPE_CHECKING = True.
"""
from importlib import reload
from multiprocessing.context import Process

import lightweight.cli
import lightweight.content.content_abc
import lightweight.content.copies
import lightweight.content.jinja_page
import lightweight.content.lwmd
import lightweight.content.md_page
import lightweight.content.sass_scss
import lightweight.errors
import lightweight.files
import lightweight.generation.context
import lightweight.generation.path
import lightweight.generation.task
import lightweight.included
import lightweight.lw
import lightweight.server
import lightweight.site
import lightweight.templates


def cover_type_checking():
    import typing
    typing.TYPE_CHECKING = True

    reload(lightweight.content.content_abc)
    reload(lightweight.content.copies)
    reload(lightweight.content.jinja_page)
    reload(lightweight.content.lwmd)
    reload(lightweight.content.md_page)
    reload(lightweight.content.sass_scss)

    reload(lightweight.generation.context)
    reload(lightweight.generation.path)
    reload(lightweight.generation.task)

    reload(lightweight.cli)
    reload(lightweight.errors)
    reload(lightweight.files)
    reload(lightweight.included)
    reload(lightweight.lw)
    reload(lightweight.server)
    reload(lightweight.site)
    reload(lightweight.template)


def test_cover_type_checking():
    """Doing this in separate process because classes change memory addresses breaking instance checks, etc"""
    p = Process(target=cover_type_checking)
    p.start()
    p.join()
