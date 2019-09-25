from __future__ import annotations

from lightweight import Site, markdown, paths, render, template, sass, feeds


def blog_posts():
    post_template = template('blog-post.html')
    return (markdown(path, post_template) for path in paths('posts/**.md'))


def main():
    site = Site(url='https://example.com')

    # Render Jinja template.
    site.include('index.html', render('pages/index.html'))

    # Render markdown blog posts.
    [site.include(f'posts/{post.filename.stem}.html', post) for post in blog_posts()]
    site.include('posts.html', render('pages/posts.html'))

    # Syndicate RSS and Atom feeds.
    [site.include(f'posts.{type}.xml', feed) for type, feed in feeds(site['posts'])]

    # Render SASS to CSS.
    site.include('static/css/style.css', sass('static/scss/lightweight.scss'))

    # Include directory with its contents.
    site.include('static/img')

    site.render()


if __name__ == '__main__':
    main()
