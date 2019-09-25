# Using Lightweight

Wow, such ease:
```python
from lightweight import Site, markdown, paths

def blog_posts(site):
    template = site.template('blog-post.html')
    return (markdown(path, template) for path in paths('posts/**.md'))


site = Site('https://example.org')

site.include('index.html')
[site.include(f'post/{post.filename.stem}.html', post) for post in blog_posts(site)]
site.include('static')

site.render()
```