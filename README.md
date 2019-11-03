# lightweight
[![PyPI](https://img.shields.io/pypi/v/lightweight)][pypi]
[![Build Status](https://img.shields.io/azure-devops/build/misha-drachuk/lightweight/8)](https://dev.azure.com/misha-drachuk/lightweight/_build/latest?definitionId=8&branchName=master)
[![Test Coverage](https://img.shields.io/coveralls/github/mdrachuk/lightweight/master)](https://coveralls.io/github/mdrachuk/lightweight)
[![Supported Python](https://img.shields.io/pypi/pyversions/lightweight)][pypi]
[![Documentation](https://img.shields.io/readthedocs/lightweight)][docs]

Static site generator i actually can use.

[Documentation][docs]


## Features
- [x] Clean and easily extensible API 
- [x] Jinja2 templates
- [x] Markdown rendering
- [ ] Markdown links
- [x] Sass/SCSS rendering
- [x] RSS/Atom feeds
- [ ] Dev server

## Installation
Available from [PyPI][pypi]:
```shell
pip install lightweight
```

## Quick Example
```python
from lightweight import Site, markdown, paths, render, template, feeds, sass


def blog_posts():
    post_template = template('blog-post.html')
    # Use globs to select files.
    return (markdown(path, post_template) for path in paths('posts/**.md'))


site = Site(url='https://example.com')

# Render a Jinja2 template.
site.include('index.html', render('pages/index.html')) 

# Render list of Markdown files.
site.include('posts.html', render('pages/posts.html'))
[site.include(f'posts/{post.filename.stem}.html', post) for post in blog_posts()]

# Syndicate RSS and Atom feeds.
[site.include(f'posts.{type}.xml', feed) for type, feed in feeds(site['posts'])]

# Render SCSS.
site.include('css/style.css', sass('styles/style.scss'))

# Include a copy of a directory.
site.include('img')
site.include('js')

# Execute all included content. 
site.render()
```

## Dev Server

Lightweight includes a simple static web server with live reload 
serving at `0.0.0.0:8080` (can be accessed via `localhost:8080`):
```bash
python -m lightweight.server <directory>
```

The live reload can be disabled with `--no-live-reload` flag:
```bash
python -m lightweight.server <directory> --no-live-reload
```

Host and port can be set via:
```bash
python -m lightweight.server <directory> --host 0.0.0.0 --port 8080
```

To stop the server press `Ctrl+C` in terminal.


[pypi]: https://pypi.org/project/lightweight/
[docs]: https://lightweight.readthedocs.io/en/latest/ 
