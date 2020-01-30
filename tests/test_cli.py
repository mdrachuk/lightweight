import asyncio
import shlex
import sys
from functools import partial
from pathlib import Path
from threading import Thread

import pytest
from pytest import fixture

from lightweight import directory, __version__, lw
from lightweight.lw import main, start_server, parse_args
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

    def test_generate(self, out: Path):
        run_cli('lw init my-project --url https://example.org/')
        project = out / 'my-project'
        assert (project / 'run.py').exists()
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
        run_cli('lw init my-project --url https://example.org/')
        sys.argv = shlex.split(f'lw serve run:dev --source my-project --port {unused_tcp_port} --no-live-reload')
        args = parse_args()
        loop = asyncio.new_event_loop()
        t = ServeThread(partial(start_server,
                                args.executable,
                                source=args.source,
                                out=args.out,
                                host=args.host,
                                port=args.port,
                                enable_reload=not args.no_live_reload,
                                loop=loop))
        t.start()
        asyncio.run(asyncio.sleep(0.2))
        response = asyncio.run(get(f'http://localhost:{unused_tcp_port}'))

        assert 'HTTP/1.0 200' in response
        assert '<!DOCTYPE html>' in response
        assert 'my-project' in response
        assert 'liveReload.start();' not in response
        assert '</html>' in response

        t.interrupt(loop)

    def test_serve_live_reload(self, unused_tcp_port, out):
        run_cli('lw init my-project --url https://example.org/')
        sys.argv = shlex.split(f'lw serve run:dev --source my-project --port {unused_tcp_port}')
        args = parse_args()
        loop = asyncio.new_event_loop()
        t = ServeThread(partial(start_server,
                                args.executable,
                                source=args.source,
                                out=args.out,
                                host=args.host,
                                port=args.port,
                                enable_reload=not args.no_live_reload,
                                loop=loop))
        t.start()
        asyncio.run(asyncio.sleep(0.2))
        response = asyncio.run(get(f'http://localhost:{unused_tcp_port}'))

        assert 'HTTP/1.0 200' in response
        assert 'liveReload.start();' in response

        t.interrupt(loop)

    def test_serve_invalid_signature(self, caplog):
        with pytest.raises(SystemExit):
            run_cli(f'lw serve invalid:signature0 --source site --port 12345')
        assert 'ERROR' in caplog.text
        assert 'InvalidCommand: "invalid:signature0"' in caplog.text

        with pytest.raises(SystemExit):
            run_cli(f'lw serve invalid:signature1 --source site --port 12345')
        assert 'InvalidCommand: "invalid:signature1"' in caplog.text

        with pytest.raises(SystemExit):
            run_cli(f'lw serve invalid:signature3 --source site --port 12345')
        assert 'InvalidCommand: "invalid:signature3' in caplog.text

    def test_serve_missing_method(self, caplog):
        with pytest.raises(SystemExit):
            run_cli(f'lw serve invalid:missing --source site --port 12345')
        assert 'InvalidCommand' in caplog.text
        assert 'missing method' in caplog.text

    def test_serve_not_callable(self, caplog):
        with pytest.raises(SystemExit):
            run_cli(f'lw serve invalid:obj --source site --port 12345')
        assert 'InvalidCommand: "invalid:obj' in caplog.text
        assert 'not callable' in caplog.text

    def test_serve_no_site(self, caplog):
        with pytest.raises(SystemExit):
            run_cli(f'lw serve invalid:no_site --source site --port 12345')
        assert 'InvalidCommand' in caplog.text
        assert 'did not return an instance of Site' in caplog.text

    def test_version(self, capsys):
        run_cli('lw version')
        captured = capsys.readouterr()
        assert captured.out == __version__ + '\n'
        assert captured.err == ''

    def test_help(self, capsys):
        run_cli('lw --help')
        assert_help_in_out(capsys)

    def test_no_cmd(self, capsys):
        run_cli('lw')
        assert_help_in_out(capsys)

    def test_serve_calls_start_server(self):
        called_start_server = False

        def assert_start_server_call(executable, source, out, host, port, enable_reload):
            nonlocal called_start_server
            called_start_server = True
            assert executable == 'run:dev'
            assert source == 'my-project'
            assert port == 8080
            assert host == 'localhost'
            assert out is None
            assert enable_reload

        lw.start_server = assert_start_server_call
        run_cli(f'lw serve run:dev --source my-project --port 8080')
        assert called_start_server


def assert_help_in_out(capsys):
    captured = capsys.readouterr()
    assert 'usage: lw [-h] {serve,init,version}' in captured.out
    assert captured.err == ''


def run_cli(cmd: str):
    sys.argv = shlex.split(cmd)
    try:
        main()
    except SystemExit as e:
        if e.code != 0:
            raise e


class ServeThread(Thread):
    def __init__(self, target):
        super().__init__(target=target)

    def interrupt(self, loop):
        async def exit():
            raise KeyboardInterrupt()

        loop.create_task(exit())
        self.join()
