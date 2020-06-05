"""Lightweight [Markdown][1] toolkit.

[`LwRenderer`][LwRenderer] is an implementation of the [`mistune.Renderer`][2] adding table of contents,
 and overriding some elements.

[1]: https://daringfireball.net/projects/markdown/
[2]: https://github.com/lepture/mistune/tree/v1#renderer
"""

from __future__ import annotations

from typing import List, Dict, NamedTuple, Optional

from mistune import Renderer, escape, escape_link  # type: ignore # no typings
from slugify import slugify  # type: ignore # no typings


class TocEntry(NamedTuple):
    """An entry of the [TocBuilder]."""
    slug: str
    title: str
    level: int


class TocBuilder:
    """[Table of Contents][TableOfContents] builder used by [TocMixin]. """
    entries: List[TocEntry]

    def __init__(self):
        self.entries: List[TocEntry] = []

    def append(self, entry: TocEntry):
        """Add an item to the table of contents."""
        self.entries.append(entry)

    def compile(self, level) -> TableOfContents:
        """Create a new Table of contents."""
        if not len(self.entries):
            return TableOfContents()

        min_level = min([entry.level for entry in self.entries])
        toc = TableOfContents(id='table-of-contents')

        self._fill_empty_sections(level + min_level - 1, min_level, toc.sections)
        self._fill_sections(level + min_level - 1, min_level, toc)
        return toc

    def _fill_sections(self, level, min_level, toc):
        for entry in self.entries:
            if entry.level > level:
                continue
            sections = toc.sections
            for l in range(min_level, entry.level):
                sections = sections[len(sections) - 1].sections
            sections.append(Section(entry.title, entry.slug))

    def _fill_empty_sections(self, level, min_level, sections):
        for i, entry in enumerate(self.entries):
            if entry.level > level:
                continue
            for _ in range(min_level, min(entry.level, level)):
                section = Section('', '')
                sections.append(section)
                sections = section.sections
            return


class TableOfContents:
    """Table of contents of a Markdown document.

    Composed from a list of [sections][Section].

    The `id` property is set to the root `<ul>` element.
    """
    id: Optional[str]
    sections: List[Section]

    def __init__(self, id: str = None):
        self.id = id
        self.sections = []

    @property
    def html(self) -> str:
        id = f' id="{self.id}"' if self.id else ''
        items = '\n'.join([f'<li><a href="#{s.slug}">{s.title}</a>{s.html}</li>' for s in self.sections])
        if not len(items):
            return ''
        return f'\n<ul{id}>\n{items}\n</ul>\n'

    def __iter__(self):
        return iter(self.sections)

    def __len__(self):
        return len(self.sections)


class Section(TableOfContents):
    """[Table of contents][TableOfContents] item."""
    title: str
    slug: str

    def __init__(self, title: str, slug: str):
        super().__init__()
        self.title = title
        self.slug = slug


class TocMixin(object):
    """A mixin used by [LwRenderer] compiling a [table of contents][TableOfContents].

    Note: requires calling [reset][TocMixin.reset] after rendering.
    """
    toc: TocBuilder

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.toc = TocBuilder()

    def reset(self):
        self.toc = TocBuilder()

    def header(self, text, level, raw=None):
        slug = slugify(text)
        rv = f'<h{level:d} id="{slug}">{text}</h{level:d}>\n'
        self.toc.append(TocEntry(slug, text, level))
        return rv

    def table_of_contents(self, level) -> TableOfContents:
        return self.toc.compile(level)


class LwRenderer(TocMixin, Renderer):
    """Renders Markdown overriding the following:
    - links — allows linking to other Markdown pages by their `.md` file paths.
    - images — adds `width=100%` to `<img/>` tags.

    Also provides a way to compile a [table of contents][TableOfContents] via [`LwRenderer.table_of_contents`].
    """

    def __init__(self, link_mapping: Dict[str, str]):
        super().__init__()
        self.url_mapping = link_mapping

    def link(self, link, title, text):
        if link.startswith('/'):
            without_slash = link[1:]
            if without_slash in self.url_mapping:
                link = self.url_mapping[without_slash]
        elif link in self.url_mapping:
            link = self.url_mapping[link]
        return super().link(link, title, text)

    def image(self, src, title, text):
        """Rendering a image with title and text.

        :param src: source link of the image.
        :param title: title text of the image.
        :param text: alt text of the image.
        """
        src = escape_link(src)
        text = escape(text, quote=True)
        if title:
            title = escape(title, quote=True)
            attributes = f'src="{src}" alt="{text}" title="{title}" width="100%"'
        else:
            attributes = f'src="{src}" alt="{text}" width="100%"'
        if self.options.get('use_xhtml'):
            return f'<img {attributes}/>'
        return f'<img {attributes}>'
