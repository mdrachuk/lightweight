---
title: Using Lightweight
summary: A short how-to.
created: 2019-10-10 00:00:00
order: 3
hide-toc: true
---

The core idea behind the project is "Code over configuration". 

It’s explicit and predictable. 
Site’s structure is easy to control when it is obvious from a single glance.

The best way to get a feel for Lightweight static site generation is simply to look at an example.

<!--preview-->

```python
from lightweight import Site, markdown, template, rss, atom, render, sass, paths
from datetime import datetime


def blog_posts(source: str):
    post_template = template('blog-post.html')
    return (markdown(path, post_template) for path in paths(source))


site = Site(url='http://example.org', out='generated/')

# Render an index page from Jinja2 template.
site.include('index.html', render('pages/index.html', generated=datetime.now()))

# Render markdown blog posts.
[site.include(f'posts/{post.filename.stem}.html', post) for post in blog_posts('posts/**.md')]
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

Let’s take the example apart.

### `Site()`

The central element of Lightweight API is the `Site`. 
Site is the context shared by every component when they are rendered. 
```python
site = Site(url='http://example.org', out='generated/')
```

### `site.include(location, content)`

The content is added to the Site. 
It is done via `site.include(location, content)` method, where
`location` is a string that is the path to the output file, 
and `content` is an object that has a `content.write(path)` method.  
```python
from lightweight import render

site.include('index.html', render('pages/index.html', generated=datetime.now()))
```

### `render(location) -> JinjaPage`
Here `render(template_location, **params)` takes a Jinja2 template location, 
and keyword arguments that are passed to the template when it is rendered.

The template is not rendered right away. 
Instead a `JinjaPage` instance is created, which is rendered and stored upon `site.render()` .

### `paths(glob) -> List[Path]`
Use `paths(glob)` when you need to list multiple files by glob.
The pattern will be searched for recursively and return a 
[`List[Path]`](https://docs.python.org/3/library/pathlib.html#pathlib.Path):
```python
all_kitten_images = paths('kittens/**/*.png')
```

### `markdown(location, template) -> MarkdownPage`
Next up rendering blog posts from markdown:
```python
from lightweight import markdown, template, paths

def blog_posts(glob: str):
    post_template = template('blog-post.html')
    return (markdown(path, post_template) for path in paths(glob))

[site.include(f'posts/{post.filename.stem}.html', post) for post in blog_posts('posts/**.md')]
```

Each file matching `posts/**.md` is passed to `markdown(...)`.
This creates a `MarkdownPage` object.

Upon `site.render()` the markdown will be rendered into the template and saved as a corresponding html.
  
### `atom(collection)`/`rss(collection) -> Feed`
Collections are created for content manipulation and aggregation. 
`ContentCollection` supports indexing, iteration, sorting, etc.

A great example is how Atom and RSS feeds are created from everything included under site’s `posts` directory.
```python
from lightweight import atom, rss

site.include('posts.atom.xml', atom(site['posts']))
site.include('posts.rss.xml', rss(site['posts']))
```

### `sass(location) -> Sass`
Why would someone use CSS when there is Sass?

```python
from lightweight import sass

site.include('lightweight.css', sass('styles/lightweight.scss')) 
```

### `site.include(glob)`
A single parameter `.include(...)` shorthand adds all files matching a glob:
```python
site.include('js')
site.include('images')
```

### `site.render()`
The last step is to collect all the content and write it to the `out` directory provided to `Site(out=...)` constructor.
```python
site.render()
``` 