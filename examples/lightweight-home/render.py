from __future__ import annotations

from argparse import ArgumentParser

from locate_lightweight_for_example import *
from lightweight import Site, markdown, paths, render, template, sass, atom, rss


def blog_posts(source: str):
    post_template = template('blog-post.html')
    return (markdown(path, post_template) for path in paths(source))


def main(dev: bool = False):
    site = Site(url='http://localhost:8080' if dev else 'http://example.org')

    # Render an index page from Jinja2 template.
    site.include('index.html', render('pages/index.html'))

    # Render markdown blog posts.
    [site.include(f'posts/{post.filename.stem}.html', post) for post in blog_posts('posts/**.md')]
    site.include('posts.html', render('pages/posts.html'))

    # Syndicate RSS and Atom feeds.
    site.include('posts.atom.xml', atom(site['posts']))
    site.include('posts.rss.xml', rss(site['posts']))

    # Render SASS to CSS.
    site.include('styles/lightweight.css', sass('styles/lightweight.scss'))

    # Include directory with its contents.
    site.include('js')
    site.include('images')

    site.render()


parser = ArgumentParser(description='Render a static website')
parser.add_argument('--dev', action='store_true', default=False, help='dev configuration')

if __name__ == '__main__':
    args = parser.parse_args()
    main(dev=args.dev)
