from __future__ import annotations

from lightweight import Site, markdown, paths, render, template, sass, feeds
from lightweight.template import jinja


def blog_posts():
    post_template = template('blog-post.html')
    return (markdown(path, post_template) for path in paths('posts/**.md'))


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
    site.include('styles/lightweight.css', sass('styles/lightweight.scss'))

    # Include directory with its contents.
    site.include('js')
    site.include('images')

    site.render()

    jinja.globals['DEV_ENVIRONMENT'] = False


if __name__ == '__main__':
    dev()
