---
title: Using Lightweight
summary: A short how-to.
created: 2019-10-10 00:00:00
---
Wow, such ease:
```python
from lightweight import Site, markdown, template, rss, atom, render, sass

site = Site(url='https://example.org')

# Render an index page from Jinja2 template.
site.include('index.html', render('pages/index.html'))

post_template = template('blog-post.html')
# Render markdown blog posts.
site.include('posts/hello.html', markdown('posts/hello-world.md', post_template))
site.include('posts/introduction.html', markdown('posts/introduction.md', post_template))
site.include('posts/future.html', markdown('posts/future-plans.md', post_template))
site.include('posts.html', render('pages/posts.html'))

# Syndicate RSS and Atom feeds.
site.include('posts.atom.xml', atom(site['posts']))
site.include('posts.rss.xml', rss(site['posts']))

# Render SASS to CSS.
site.include('lightweight.css', sass('styles/lightweight.scss'))

# Include directory with its contents.
site.include('js')
site.include('images')

site.render()
```