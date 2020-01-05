from os import chdir, getcwd
from pathlib import Path

import pytest
from jinja2 import TemplateNotFound

from lightweight import Site, jinja, Content, directory, GenContext, GenPath


def test_render_jinja(tmp_path: Path):
    src_location = 'resources/jinja/title.html'
    out_location = 'title.html'

    test_out = tmp_path / 'out'
    site = Site(url='https://example.com')

    site.include(out_location, jinja(src_location, title='99 reasons lightweight rules'))
    site.generate(test_out)

    assert (test_out / out_location).exists()
    with open('expected/jinja/params.html') as expected:
        assert (test_out / out_location).read_text() == expected.read()


def test_render_jinja_file(tmp_path: Path):
    src_location = 'resources/jinja/file.html'
    out_location = 'jinja/file.html'

    test_out = tmp_path / 'out'
    site = Site(url='https://example.com')

    site.include(out_location, jinja(src_location))
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


def test_resolves_sub_site_template_by_cwd(tmp_path: Path):
    site = Site('http://example.org')
    with directory('site'):
        subsite = Site('http://example.org')
        subsite.include('page.html', jinja('page.html'))
    site.include('subsite', subsite)
    site.generate(out=tmp_path)

    with open('expected/subsite/page.html') as expected:
        assert (tmp_path / 'subsite' / 'page.html').read_text() == expected.read()
