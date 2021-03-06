import asyncio
from os import chdir, getcwd
from pathlib import Path

import pytest
from jinja2 import TemplateNotFound, UndefinedError

from lightweight import Site, jinja, Content, directory, GenContext, GenPath, from_ctx, jinja_env


def test_render_jinja(tmp_path: Path):
    src_location = 'resources/jinja/title.html'
    out_location = 'title.html'

    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')

    site.add(out_location, jinja(src_location, title='99 reasons lightweight rules'))
    site.generate(test_out)

    assert (test_out / out_location).exists()
    with open('expected/jinja/params.html') as expected:
        assert (test_out / out_location).read_text() == expected.read()


def test_render_jinja_file(tmp_path: Path):
    src_location = 'resources/jinja/file.html'
    out_location = 'jinja/file.html'

    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')

    site.add(out_location, jinja(src_location))
    site.generate(test_out)

    assert (test_out / out_location).exists()
    with open('expected/jinja/file.html') as expected:
        assert (test_out / out_location).read_text() == expected.read()


class NoopContent(Content):
    def write(self, path: GenPath, ctx: GenContext):
        """
        :param ctx:
        """


class TestWorkingDirectory:

    def setup_method(self, method):
        self.original_cwd = getcwd()

    def teardown_method(self, method):
        chdir(self.original_cwd)

    def test_dynamic_cwd(self, tmp_path: Path):
        assert jinja('templates/test.html')
        chdir('templates')
        assert jinja('test.html')
        with pytest.raises(TemplateNotFound):
            jinja('templates/test.html')


def test_lazy_params(tmp_path: Path):
    src_location = 'resources/jinja/lazy.html'
    out_location = 'lazy.html'

    test_out = tmp_path / 'out'
    site = Site(url='https://example.org/')

    site.add(out_location, jinja(src_location, lazy=from_ctx(lambda ctx: f'Hello there! {ctx.tasks[0].path}')))
    site.generate(test_out)

    assert (test_out / out_location).exists()
    with open('expected/jinja/lazy.html') as expected:
        assert (test_out / out_location).read_text() == expected.read()


def test_jinja_env_does_not_allow_undefined():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with pytest.raises(UndefinedError):
        jinja_env.from_string('{{something}}').render()
