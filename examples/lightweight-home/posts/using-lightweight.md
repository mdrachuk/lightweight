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
[site.include(f'posts/{post.path.stem}.html', post) for post in blog_posts('posts/**.md')]
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

Let’s take it apart.

### `Site()`

The central element of Lightweight API is the `Site`.
Site is a collection of content and the context provided to content when it is rendered. 
```python
site = Site(url='http://example.org', out='generated/')
```

### `site.include(location, content)`

The API is designed to look declarative with every line defining the target location and the content.
 
It is done via `site.include(location, content)` method,
where `location` is a string path to the output file, 
and `content` is an object that has a `content.write(path)` method.

The beauty is in the fact that every line ends up having 
the source, the target and the transformation from former to latter:

```python
site.include(<output location>, <transformation>(<source location>, **options))
```  

### `render(location) -> JinjaPage`
```python
from lightweight import render

site.include('index.html', render('pages/index.html', generated=datetime.now()))
```

Here `render(template_location, **params)` takes a Jinja2 template location, 
and keyword arguments that are passed to the template when it is rendered.

The template is not rendered right away. 
Instead a `JinjaPage(Content)` instance is created. 
It is rendered and stored upon `site.render()` at the very end.

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

[site.include(f'posts/{post.path.stem}.html', post) for post in blog_posts('posts/**.md')]
```

Each file matching `posts/**.md` is passed to `markdown(...)`.
This creates a `MarkdownPage` object.

Upon `site.render()` the markdown will be rendered into the template and saved as a corresponding html.
  
### `atom(collection)`/`rss(collection) -> Feed`
Collections are created for content manipulation and aggregation. 
`ContentCollection` supports indexing, iteration, etc.

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

At this point every `Content.write(path: SitePath)` is executed. 
This two step design allows to depend on the whole content tree.
