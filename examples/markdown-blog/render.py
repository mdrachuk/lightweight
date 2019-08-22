from __future__ import annotations

import os
import sys
from pathlib import Path


def _fix_path():
    _fp = Path(os.path.realpath(__file__))
    os.chdir(_fp.parent)
    sys.path.append(str(_fp.parent.parent.parent))


# FIXME: This is only to run from inside of "lightweight" repository.
_fix_path()

from lightweight import Site, markdown, paths


def blog_posts(site):
    template = site.template('blog-post.html')
    return (markdown(path, template) for path in paths('blog/**.md'))


def main():
    site = Site()

    site.include('index.html')
    [site.include(f'post/{post.name}.html', post) for post in blog_posts(site)]
    site.include('static')

    site.render()


if __name__ == '__main__':
    main()
