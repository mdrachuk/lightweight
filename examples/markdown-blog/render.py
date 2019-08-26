from __future__ import annotations

from locate_lightweight_for_example import *  # FIXME: This is only to run from inside of "lightweight" repository.

from lightweight import Site, markdown, paths, render, template


def blog_posts():
    post_template = template('blog-post.html')
    return (markdown(path, post_template) for path in paths('blog/**.md'))


def main():
    site = Site()

    site.include(render('index.html'))
    [site.include(f'posts/{post.name}.html', post) for post in blog_posts()]
    site.include('static')

    site.render()


if __name__ == '__main__':
    main()
