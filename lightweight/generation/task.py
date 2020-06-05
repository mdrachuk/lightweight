from dataclasses import dataclass

from lightweight import Content

from .path import GenPath
from .context import GenContext


@dataclass(frozen=True)
class GenTask:
    """A task executed by [Site][lightweight.Site] during generation.

    All of site’s tasks can be accessed during generation via [GenContext][GenContext.tasks].

    Generation Task objects differ from the [Site’s IncludedContent][lightweight.site.IncludedContent]
    by having the path of [GenPath] type (instead of regular Path).
    [GenPath] has knowledge of the generation `out` directory,
    and is passed directly to [`content.write(path, ctx)`][Content.write].

    Includes `cwd` (current working directory) in which the original content was created.
    Content [`write(...)`][Content.write] operates from this directory.
    """
    path: GenPath
    ctx: GenContext
    content: Content
    cwd: str  # current working directory
