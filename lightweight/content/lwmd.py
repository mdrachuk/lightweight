from __future__ import annotations

from collections import namedtuple
from typing import List, Dict

import mistune  # type: ignore # no typings
from slugify import slugify  # type: ignore # no typings

TocEntry = namedtuple('TocEntry', ['slug', 'text', 'level'])


class TocMixin(object):
    toc_entries: List[TocEntry]

    def reset(self):
        self.toc_entries = []

    def header(self, text, level, raw=None):
        slug = slugify(text)
        rv = f'<h{level:d} id="{slug}">{text}</h{level:d}>\n'
        self.toc_entries.append(TocEntry(slug, text, level))
        return rv

    def render_toc(self, level=3):
        toc_items = list(self._iter_toc(level))
        if len(toc_items) < 5:
            return ''
        return ''.join(self._iter_toc(level))

    def _iter_toc(self, level):
        # TODO:mdrachuk:9/26/19: return structured model of ToC instead of HTML. Let users define how to render it.
        first_level = 0
        last_level = 0

        yield '<ul id="table-of-content">\n'

        for entry in self.toc_entries:
            slug, text, cur_level = entry

            if cur_level > level:
                # ignore this level
                continue

            if first_level == 0:
                # based on first level
                first_level = cur_level
                last_level = cur_level
                yield f'<li><a href="#{slug}">{text}</a>'
            elif last_level == cur_level:
                yield f'</li>\n<li><a href="#{slug}">{text}</a>'
            elif last_level == cur_level - 1:
                last_level = cur_level
                yield f'\n<ul>\n<li><a href="#{slug}">{text}</a>'
            elif last_level > cur_level:
                # close indention
                yield '</li>'
                while last_level > cur_level:
                    yield '</ul>\n</li>\n'
                    last_level -= 1
                yield f'<li><a href="#{slug}">{text}</a>'

        # close tags
        yield '</li>\n'
        while last_level > first_level:
            yield '</ul>\n</li>\n'
            last_level -= 1

        yield '</ul>\n'


class LwRenderer(TocMixin, mistune.Renderer):

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


class LwMarkdown(mistune.Markdown):
    def __init__(self, renderer: mistune.Renderer):
        super().__init__(renderer=renderer)

    def render(self, text):
        self.renderer.reset()
        html = super().render(text)
        toc_html = self.renderer.render_toc(level=3)
        return html, toc_html
