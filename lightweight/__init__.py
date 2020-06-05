"""Lightweight is a "Code over configuration" static site generator.

```python
from lightweight import Site, markdown, paths, jinja, template, rss, atom, sass


def blog_posts(source):
    post_template = template('posts/_template.html')
    # Use globs to select files. # source = 'posts/**.md'
    return (markdown(path, post_template) for path in paths(source))


site = Site(url='https://example.org/')

# Render an index page from Jinja2 template.
site.include('index.html', jinja('pages/index.html'))

# Render markdown blog posts.
[site.include(f'posts/{post.source_path.stem}.html', post) for post in blog_posts('posts/**.md')]
site.include('posts.html', jinja('pages/posts.html'))

# Render SASS to CSS.
site.include('css/style.css', sass('styles/style.scss'))

# Include a copy of a directory.
site.include('img')
site.include('js')

# Execute all included content.
site.generate()
```
"""
import logging

from .content import Content, markdown, jinja, from_ctx, sass
from .files import paths, directory
from .generation import GenPath, GenContext
from .site import Site
from .templates import template, jinja_env
from .cli import SiteCli

logging.basicConfig()
logger = logging.getLogger('lw')
logger.setLevel(logging.INFO)

__version__ = '1.0.0.dev50'
