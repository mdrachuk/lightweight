"""
The import like
if TYPE_CHECKING:
    import bla_bla

Only covered after reloading module with TYPE_CHECKING = True.
"""
from importlib import reload
from multiprocessing.context import Process

import lightweight.cli
import lightweight.content.content_
import lightweight.content.copies_
import lightweight.content.jinja_
import lightweight.content.lwmd_
import lightweight.content.markdown_
import lightweight.content.sass_
import lightweight.errors
import lightweight.files
import lightweight.generation.context
import lightweight.generation.path
import lightweight.generation.task
import lightweight.included
import lightweight.lw
import lightweight.server
import lightweight.site
import lightweight.template


def cover_type_checking():
    import typing
    typing.TYPE_CHECKING = True

    reload(lightweight.content.content_)
    reload(lightweight.content.copies_)
    reload(lightweight.content.jinja_)
    reload(lightweight.content.lwmd_)
    reload(lightweight.content.markdown_)
    reload(lightweight.content.sass_)

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
