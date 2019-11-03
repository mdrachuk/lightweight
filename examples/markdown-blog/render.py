from __future__ import annotations

from locate_lightweight_for_example import *
from lightweight import Site, markdown, paths, render, template, sass, atom, rss


def blog_posts():
    post_template = template('blog-post.html')
    return (markdown(path, post_template) for path in paths('posts/**.md'))


def dev():
    site = Site(url='http://localhost:8080')

    # Render an index page from Jinja2 template.
    site.include('index.html', render('pages/index.html'))

    # Render markdown blog posts.
    [site.include(f'posts/{post.filename.stem}.html', post) for post in blog_posts()]
    site.include('posts.html', render('pages/posts.html'))

    # Syndicate RSS and Atom feeds.
    site.include(f'posts.atom.xml', atom(site['posts']))
    site.include(f'posts.rss.xml', rss(site['posts']))

    # Render SASS to CSS.
    site.include('styles/lightweight.css', sass('styles/lightweight.scss'))

    # Include directory with its contents.
    site.include('js')
    site.include('images')

    site.render()


if __name__ == '__main__':
    dev()
