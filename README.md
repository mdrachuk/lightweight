# lightweight
[![PyPI](https://img.shields.io/pypi/v/lightweight)][pypi]
[![Build Status](https://img.shields.io/azure-devops/build/misha-drachuk/lightweight/8)](https://dev.azure.com/misha-drachuk/lightweight/_build/latest?definitionId=8&branchName=master)
[![Test Coverage](https://img.shields.io/coveralls/github/mdrachuk/lightweight/master)](https://coveralls.io/github/mdrachuk/lightweight)
[![Supported Python](https://img.shields.io/pypi/pyversions/lightweight)][pypi]
[![Documentation](https://img.shields.io/readthedocs/lightweight)][docs]

Static site generator i actually can use.

[Documentation][docs]


## Features
- Clean and easily extensible API 
- [x] Jinja2 templates
- [x] Markdown rendering
- [ ] Markdown links
- [x] Sass/SCSS rendering
- [ ] RSS/Atom feeds

## Installation
Available from [PyPI][pypi]:
```shell
pip install lightweight
```

## Quick Example
```python

from lightweight import Site, markdown, paths, render, template, sass


def blog_posts():
    post_template = template('blog-post.html')
    return (markdown(path, post_template) for path in paths('blog/**.md'))


site = Site()

site.include(render('index.html'))
[site.include(f'posts/{post.file.name}.html', post) for post in blog_posts()]
site.include('static/css/style.css', sass('static/scss/lightweight.scss'))
site.include('static/img')

site.render()
```

[pypi]: https://pypi.org/project/lightweight/
[docs]: https://lightweight.readthedocs.io/en/latest/ 
