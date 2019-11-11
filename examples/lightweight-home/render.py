from __future__ import annotations

from argparse import ArgumentParser

from locate_lightweight_for_example import update_path

update_path()

from lightweight import Site, markdown, paths, jinja, template, sass, atom, rss
from lightweight.content.lwmd import LwRenderer


class WrapLinks(LwRenderer):

    def link(self, link, title, text):
        text = f'<span>{text}</span>'
        return super(WrapLinks, self).link(link, title, text)


def blog_posts(source: str):
    post_template = template('blog-post.html')
    return (markdown(path, post_template, renderer=WrapLinks) for path in paths(source))


def main(dev: bool = False):
    site = Site(url='http://localhost:8080' if dev else 'http://example.org')

    # Render an index page from Jinja2 template.
    site.include('index.html', jinja('pages/index.html'))

    # Render markdown blog posts.
    [site.include(f'posts/{post.path.stem}.html', post) for post in blog_posts('posts/**.md')]
    site.include('posts.html', jinja('pages/posts.html'))

    # Syndicate RSS and Atom feeds.
    site.include('posts.atom.xml', atom(site['posts']))
    site.include('posts.rss.xml', rss(site['posts']))

    # Render SASS to CSS.
    site.include('lightweight.css', sass('styles/lightweight.scss'))

    # Include directory with its contents.
    site.include('js')
    site.include('images')

    site.render()


parser = ArgumentParser(description='Render a static website')
parser.add_argument('--dev', action='store_true', default=False, help='dev configuration')

if __name__ == '__main__':
    args = parser.parse_args()
    main(dev=args.dev)
