"""Render [Jinja templates][1] in place of Lightweight [Content].

[1]: https://jinja.palletsprojects.com/en/2.11.x/
"""

from __future__ import annotations

__all__ = ['JinjaPage', 'jinja', 'from_ctx']

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Union, TYPE_CHECKING, Callable, TypeVar, Generic

from jinja2 import Template

from .content_abc import Content
from ..templates import template

if TYPE_CHECKING:
    from lightweight import GenPath, GenContext


@dataclass(frozen=True)
class JinjaPage(Content):
    """Content rendered from a Jinja Template."""

    template: Template = field(repr=False)
    source_path: Path
    props: Dict[str, Any] = field(repr=False)

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
        props = {key: _eval_if_lazy(value, ctx) for key, value in self.props.items()}
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


T = TypeVar('T')


class LazyContextParameter(Generic[T]):
    """A decorator for Jinja template parameters lazily evaluated from [context][GenContext] during render. """

    def __init__(self, func: Callable[[GenContext], T]):
        self.func = func

    def __call__(self, ctx: GenContext) -> T:
        return self.func(ctx)  # type: ignore


def from_ctx(func: Callable[[GenContext], T]) -> Callable[[GenContext], T]:
    """Evaluate the provided function lazily from context at the point of generation.

    ```python
    from lightweight import jinja, from_ctx

    ...

    def post_tasks(ctx: GenContext):
        return [task for task in ctx.tasks if task.path.parts[0] == 'posts']

    ...

    site.add('posts', jinja('posts.html', posts=from_ctx(post_tasks)))
    ```
    """
    return LazyContextParameter(func)


def _eval_if_lazy(o: Any, ctx: GenContext) -> Any:
    """If passed a [lazy parameter][LazyContextParameter] the result of its evaluation.
    Otherwise, returns the provided value."""

    if isinstance(o, LazyContextParameter):
        return o(ctx)
    return o
