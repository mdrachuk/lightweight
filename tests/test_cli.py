import asyncio
import shlex
import subprocess
import sys
import time
from os import getcwd
from pathlib import Path

import pytest
from pytest import fixture

from lightweight import directory, __version__, lw, Site, SiteCli, jinja
from lightweight.errors import InvalidSiteCliUsage, InvalidCommand
from lightweight.lw import FailedGeneration, start_server
from tests.server_utils import get


class TestTheCli:

    @fixture(autouse=True)
    def _recover_args(self):
        argv = sys.argv
        yield
        sys.argv = argv

    @fixture(autouse=True)
    def _recover_start_server(self):
        m = lw.start_server
        yield
        lw.start_server = m

    @fixture
    def out(self, tmp_path):
        with directory(tmp_path):
            yield tmp_path

    @fixture
    def mock_start_server(self):
        mock = MockStartServer()
        import lightweight.cli
        original = lightweight.cli.start_server
        lightweight.cli.start_server = mock
        yield mock
        lightweight.cli.start_server = original

    def test_generate(self, out: Path):
        run_lw('lw init my-project')
        project = out / 'my-project'
        assert (project / 'website.py').exists()
        assert (project / '_templates_').exists()
        assert (project / 'img').exists()
        assert (project / 'js').exists()
        assert (project / 'posts').exists()
        assert (project / 'styles').exists()
        assert (project / 'blog.html').exists()
        assert (project / 'index.html').exists()
        assert (project / 'labs.html').exists()
        assert (project / 'requirements.txt').exists()
        # TODO:mdrachuk:27.01.2020: check that output is the same

    def test_serve(self, unused_tcp_port, out):
        run_lw('lw init my-project')
        cmd = shlex.split(f'python my-project/website.py serve '
                          f'--watch my-project '
                          f'--port {unused_tcp_port} '
                          f'--no-live-reload')
        p = subprocess.Popen(cmd)
        time.sleep(1)
        response = asyncio.run(get(f'http://localhost:{unused_tcp_port}'))

        assert 'HTTP/1.0 200' in response
        assert '<!DOCTYPE html>' in response
        assert 'my-project' in response
        assert 'liveReload.start();' not in response
        assert '</html>' in response

        p.kill()

    def test_serve_live_reload(self, unused_tcp_port, out, event_loop):
        run_lw('lw init my-project')
        cmd = shlex.split(f'python my-project/website.py serve '
                          f'--watch my-project '
                          f'--port {unused_tcp_port} ')
        p = subprocess.Popen(cmd)

        time.sleep(1)
        response = asyncio.run(get(f'http://localhost:{unused_tcp_port}'))

        assert 'HTTP/1.0 200' in response
        assert 'liveReload.start();' in response

        p.kill()

    def test_version(self, capsys):
        run_lw('lw version')
        captured = capsys.readouterr()
        assert captured.out == __version__ + '\n'
        assert captured.err == ''

    def test_help(self, capsys):
        run_lw('lw --help')
        assert_help_in_out(capsys)

    def test_no_cmd(self, capsys):
        run_lw('lw')
        assert_help_in_out(capsys)

    def test_site_cli_serve(self, mock_start_server):
        mock = mock_start_server
        run_site_cli("test_cli.py serve")
        assert mock.run_count == 1
        assert mock.last_args[0] == Path(__file__)
        assert mock.last_args[1] == 'build_func'
        assert len(mock.last_kwargs) == 5
        assert mock.last_kwargs['source'] == Path(__file__).parent
        assert mock.last_kwargs['out'] == Path(getcwd()) / 'out'
        assert mock.last_kwargs['host'] == 'localhost'
        assert mock.last_kwargs['port'] == 8080
        assert mock.last_kwargs['enable_reload'] is True

    def test_site_cli_custom_serve(self, mock_start_server):
        mock = mock_start_server
        run_site_cli("test_cli.py serve "
                     "--watch this "
                     "--out stout "
                     "--host 0.0.0.0 "
                     "--port 1212 "
                     "--no-live-reload")
        assert mock.run_count == 1
        assert mock.last_args[0] == Path(__file__)
        assert mock.last_args[1] == 'build_func'
        assert len(mock.last_kwargs) == 5
        assert mock.last_kwargs['source'] == Path('this')
        assert mock.last_kwargs['out'] == Path('stout')
        assert mock.last_kwargs['host'] == '0.0.0.0'
        assert mock.last_kwargs['port'] == 1212
        assert mock.last_kwargs['enable_reload'] is False

    def test_exit_on_failed_generation(self, mock_start_server):
        def raise_failed(*args, **kwargs):
            raise FailedGeneration()

        mock = mock_start_server
        mock.doing(raise_failed)
        run_site_cli("test_cli.py serve")
        assert mock.run_count == 1

    def test_cant_serve_uncallable(self):
        with pytest.raises(InvalidSiteCliUsage):
            run_site_cli("test_cli.py serve", build='a')

    def test_serve_wrong_callable(self):
        with pytest.raises(InvalidSiteCliUsage):
            run_site_cli("test_cli.py serve", build=lambda: None)

    def test_cant_serve_method(self):
        class Some:
            def method(self):
                pass

        with pytest.raises(InvalidSiteCliUsage):
            run_site_cli("test_cli.py serve", build=Some().method)

    def test_serve_invalid_signature(self, mock_start_server):
        with pytest.raises(InvalidSiteCliUsage):
            run_site_cli("test_cli.py serve", build=build_func_no_arg)
        with pytest.raises(InvalidSiteCliUsage):
            run_site_cli("test_cli.py serve", build=build_func_2_args)
        run_site_cli("test_cli.py serve", build=build_func_with_default)

    def test_invalid_command_shows_help(self, capsys):
        run_site_cli("test_cli.py")
        assert "usage: test_cli.py" in capsys.readouterr().out

    def test_build(self, mock_start_server, tmp_path: Path):
        with directory(tmp_path):
            index = tmp_path / 'index'
            index.write_text('{{ site }}')
            run_site_cli("test_cli.py build", build=build_jinja_file)
            result = tmp_path / 'out' / 'index'
            assert result.read_text() == "http://localhost:8080/"

    def test_build_url(self, mock_start_server, tmp_path: Path):
        with directory(tmp_path):
            index = tmp_path / 'index'
            index.write_text('{{ site }}')
            run_site_cli("test_cli.py build --url https://example.com/", build=build_jinja_file)
            result = tmp_path / 'out' / 'index'
            assert result.read_text() == "https://example.com/"

    def test_build_out(self, mock_start_server, tmp_path: Path):
        with directory(tmp_path):
            index = tmp_path / 'index'
            index.write_text('{{ site }}')
            run_site_cli("test_cli.py build --out of-here", build=build_jinja_file)
            result = tmp_path / 'of-here' / 'index'
            assert result.read_text() == "http://localhost:8080/"

    def test_build_host_port(self, mock_start_server, tmp_path: Path):
        with directory(tmp_path):
            index = tmp_path / 'index'
            index.write_text('{{ site }}')
            run_site_cli("test_cli.py build --host 0.0.0.0 --port 69", build=build_jinja_file)
            result = tmp_path / 'out' / 'index'
            assert result.read_text() == "http://0.0.0.0:69/"

    def test_build_error_with_url_and_host(self, mock_start_server):
        with pytest.raises(InvalidCommand):
            run_site_cli("test_cli.py build --host 0.0.0.0 --url http://example.org/")

    def test_build_error_with_url_and_port(self, mock_start_server):
        with pytest.raises(InvalidCommand):
            run_site_cli("test_cli.py build --port 42 --url http://example.org/")

    def test_run_server(self, tmp_path):
        def raise_interrupt():
            raise SystemExit()

        loop = asyncio.new_event_loop()
        loop.run_forever = raise_interrupt
        with pytest.raises(SystemExit):
            start_server(Path(__file__), 'build_func', source=tmp_path, out=tmp_path / 'out', host='localhost',
                         port=8080, enable_reload=False, loop=loop)


def assert_help_in_out(capsys):
    captured = capsys.readouterr()
    assert 'usage: lw [-h] {init,version}' in captured.out
    assert captured.err == ''


def run_lw(cmd: str):
    sys.argv = shlex.split(cmd)
    try:
        lw.main()
    except SystemExit as e:
        if e.code != 0:
            raise e


def run_site_cli(cmd: str, build=None):
    sys.argv = shlex.split(cmd)
    try:
        cli = SiteCli(build or build_func)
        cli.run()
    except SystemExit as e:
        if e.code != 0:
            raise e


def interrupt(loop):
    async def _interrupt():
        raise KeyboardInterrupt()

    loop.create_task(_interrupt())


def build_func(url):
    return Site(url=url)


def build_jinja_file(url):
    site = Site(url=url)
    site.include('index', jinja('index'))
    return site


def build_func_no_arg():
    return Site(url='http://test-cli.py/')


def build_func_2_args(a, b):
    return Site(url='http://test-cli.py/')


def build_func_with_default(a, b='test'):
    return Site(url='http://test-cli.py/')


class MockStartServer:
    def __init__(self):
        self.run_count = 0
        self.last_args = None
        self.last_kwargs = None
        self._implementation = self.noop_implementation

    def __call__(self, *args, **kwargs):
        self.run_count += 1
        self.last_args = list(args)
        self.last_kwargs = dict(kwargs)
        self._implementation()

    def doing(self, func):
        self._implementation = func

    @staticmethod
    def noop_implementation(*args, **kwargs):
        pass
