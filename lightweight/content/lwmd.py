from __future__ import annotations

from collections import namedtuple
from typing import List, Dict

from mistune import Renderer, escape, escape_link  # type: ignore # no typings
from slugify import slugify  # type: ignore # no typings

TocEntry = namedtuple('TocEntry', ['slug', 'title', 'level'])


class TocBuilder():
    def __init__(self):
        self.entries: List[TocEntry] = []

    def append(self, entry: TocEntry):
        self.entries.append(entry)

    def compile(self, level) -> TableOfContents:
        if not len(self.entries):
            return TableOfContents()

        min_level = min([entry.level for entry in self.entries])
        toc = TableOfContents(id='table-of-contents')

        self.fill_empty_sections(level + min_level - 1, min_level, toc.sections)
        self.fill_sections(level + min_level - 1, min_level, toc)
        return toc

    def fill_sections(self, level, min_level, toc):
        for entry in self.entries:
            if entry.level > level:
                continue
            sections = toc.sections
            for l in range(min_level, entry.level):
                sections = sections[len(sections) - 1].sections
            sections.append(Section(entry.title, entry.slug))

    def fill_empty_sections(self, level, min_level, sections):
        for i, entry in enumerate(self.entries):
            if entry.level > level:
                continue
            for _ in range(min_level, min(entry.level, level)):
                section = Section('', '')
                sections.append(section)
                sections = section.sections
            return


class TableOfContents:

    def __init__(self, id: str = None):
        self.id = id
        self.sections: List[Section] = []

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

    def __init__(self, title: str, slug: str):
        super().__init__()
        self.title = title
        self.slug = slug


class TocMixin(object):
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
