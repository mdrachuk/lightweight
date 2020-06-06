---
title: Using Lightweight
summary: A short how-to. The best way to get a feel for Lightweight static site generation is simply to look at an example...
created: 2019-11-23 00:00:00
updated: 2020-01-01 00:00:00
order: 3
hide-toc: true
---

The core idea behind the project is "Code over configuration". 

It’s explicit and predictable. <br>
Site’s structure is easy to manage when it is obvious from a single glance.

The best way to get a feel for using Lightweight is to take a look at an example.

<!--preview-->

```python
from lightweight import Site, markdown, template, rss, atom, jinja, sass, paths
from datetime import datetime


def blog_posts(source: str):
    post_template = template('_templates_/blog/post.html')
    return (markdown(path, post_template) for path in paths(source))


site = Site(url='http://example.org', title='The Example')

# Render an index page from Jinja2 template.
site.add('index.html', jinja('index.html', generated=datetime.now()))

# Render markdown blog posts.
[site.add(f'blog/{post.source_path.stem}.html', post) for post in blog_posts('posts/**.md')]
site.add('blog.html', jinja('blog.html'))

# Syndicate RSS and Atom feeds.
site.add('blog.atom.xml', atom(site['blog']))
site.add('blog.rss.xml', rss(site['blog']))

# Render SASS to CSS.
site.add('lightweight.css', sass('styles/lightweight.scss'))

# Include directory with its contents.
site.add('js')
site.add('images')

site.generate(out='generated/')
``` 

Let’s take it apart.

### `Site()`

The central element of Lightweight API is the `Site`.
Site is a collection of Content. 
```python
site = Site(url='http://example.org', title='The Example')
```

### `site.include(location, content)`

The API is designed to look declarative with every line defining the target location and the content source.
 
To achieve this most of the library is variation of `site.include(location, content)`,
where `location` is a string path to the output file, 
and `content` is an object that has a `content.write(path)` method.

The beauty is in the fact that every line ends up having 
the source, the target and the transformation from former to latter:

```python
site.add(<output location>, <transformation>(<source location>, **options))
```  

### `jinja(location) -> JinjaPage`
```python
from lightweight import jinja

site.add('index.html', jinja('pages/index.html', generated=datetime.now()))
```

Here `jinja(template_location, **params)` takes a Jinja2 template location, 
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
    post_template = template('posts/_template.html')
    return (markdown(path, post_template) for path in paths(glob))

[site.add(f'posts/{post.path.stem}.html', post) for post in blog_posts('posts/**.md')]
```

Each file matching `posts/**.md` is passed to `markdown(...)`.
This creates a `MarkdownPage` object.

Upon `site.render()` the markdown will be rendered into the template and saved as a corresponding html.
  
### `atom(site) -> AtomFeed`
### `rss(site) -> RssFeed`
Collections are created for content manipulation and aggregation. 
`ContentCollection` supports indexing, iteration, etc.

A great example is how Atom and RSS feeds are created from everything included under site’s `posts` directory.
```python
from lightweight import atom, rss

site.add('posts.atom.xml', atom(site['posts']))
site.add('posts.rss.xml', rss(site['posts']))
```

### `sass(location) -> Sass`
Why would someone use CSS when there is Sass?

```python
from lightweight import sass

site.add('lightweight.css', sass('styles/lightweight.scss')) 
```

### `site.include(glob)`
A single parameter `.include(...)` shorthand adds all files matching a glob:
```python
site.add('js')
site.add('images')
```

### `site.render()`
The last step is to collect all the content and write it to the `out` directory provided to `Site(out=...)` constructor.
```python
site.generate()
``` 

At this point every `Content.write(path: SitePath)` is executed. 
This two step design allows to depend on the whole content tree.
