from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from lightweight import Site, markdown, paths, render, template, sass, feeds, Content, SitePath
from lightweight.template import jinja


def blog_posts():
    post_template = template('blog-post.html')
    return (markdown(path, post_template) for path in paths('posts/**.md'))


@dataclass
class File(Content):
    content: str

    def render(self, path: SitePath):
        path.create(self.content)


def file(text: str) -> File:
    return File(content=text)


def dev():
    jinja.globals['DEV_ENVIRONMENT'] = True

    site = Site(url='http://localhost:8080')

    # Render an index page from Jinja2 template.
    site.include('index.html', render('pages/index.html'))

    # Render markdown blog posts.
    [site.include(f'posts/{post.filename.stem}.html', post) for post in blog_posts()]
    site.include('posts.html', render('pages/posts.html'))

    # Syndicate RSS and Atom feeds.
    [site.include(f'posts.{type}.xml', feed) for type, feed in feeds(site['posts'])]

    # Render SASS to CSS.
    site.include('static/css/lightweight.css', sass('static/scss/lightweight.scss'))

    # Include directory with its contents.
    site.include('static/js')
    site.include('static/img')

    # A unique id to queried to check if the site was updated.
    site.include('id', file(str(uuid4())))

    site.render()

    jinja.globals['DEV_ENVIRONMENT'] = False


if __name__ == '__main__':
    dev()
