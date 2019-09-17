from __future__ import annotations

from locate_lightweight_for_example import *  # FIXME: This is only to run from inside of "lightweight" repository.

from lightweight import Site, markdown, paths, render, template, sass, feeds


def blog_posts():
    post_template = template('blog-post.html')
    return (markdown(path, post_template) for path in paths('blog/**.md'))


def main():
    site = Site(url='https://example.com')

    # Render Jinja template.
    site.include(render('index.html'))

    # Render markdown blog posts.
    [site.include(f'posts/{post.file.name}.html', post) for post in blog_posts()]

    # Syndicate RSS and Atom feeds.
    [site.include(f'posts.{type}.xml', feed) for type, feed in feeds(site['posts'])]

    # Render SASS to CSS.
    site.include('static/css/style.css', sass('static/scss/lightweight.scss'))

    # Include directory with its contents.
    site.include('static/img')

    site.render()


if __name__ == '__main__':
    main()
