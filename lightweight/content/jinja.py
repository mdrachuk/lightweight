from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Union, TYPE_CHECKING, Callable

from jinja2 import Template

from .content import Content
from ..template import template

if TYPE_CHECKING:
    from lightweight import GenPath, GenContext


@dataclass(frozen=True)
class JinjaPage(Content):
    """A file rendered from a Jinja Template."""

    template: Template
    source_path: Path
    props: Dict[str, Any]

    def write(self, path: GenPath, ctx: GenContext):
        path.create(self.render(ctx))

    def render(self, ctx):
        # TODO:mdrachuk:06.01.2020: warn if site, ctx, source are in props!
        return self.template.render(
            site=ctx.site,
            ctx=ctx,
            content=self,
            **self._evaluated_props(ctx)
        )

    def _evaluated_props(self, ctx) -> Dict[str, Any]:
        props = {key: eval_if_lazy(value, ctx) for key, value in self.props.items()}
        return props


def jinja(template_path: Union[str, Path], **props) -> JinjaPage:
    """Renders the page at path with provided parameters.

    Templates are resolved from the current directory (cwd).
    """
    path = Path(template_path)
    return JinjaPage(
        template=template(path),
        source_path=path,
        props=props,
    )


class LazyContextParameter:
    """A decorator for Jinja template parameters lazily evaluated from [context][GenContext] during render. """

    def __init__(self, func: Callable[[GenContext], Any]):
        self.func = func

    def eval(self, ctx: GenContext) -> Any:
        return self.func(ctx)  # type: ignore


def from_ctx(func: Callable[[GenContext], Any]):
    """Mark a function with a decorator for its result to be evaluated lazily from context at the point of render
     and used as a Jinja template parameter.

    @example
    ```python
    from lightweight import jinja, from_ctx

    ...

    def post_tasks(ctx: GenContext):
        return [task for task in ctx.tasks if task.path.parts[0] == 'posts']

    ...

    site.include('posts', jinja('posts.html', posts=from_ctx(post_tasks)))
    ```
    """
    return LazyContextParameter(func)


def eval_if_lazy(o: Any, ctx: GenContext) -> Any:
    """If passed a [lazy parameter][LazyContextParameter] the result of its evaluation.
    Otherwise, returns the provided value."""
    if isinstance(o, LazyContextParameter):
        return o.eval(ctx)
    return o
