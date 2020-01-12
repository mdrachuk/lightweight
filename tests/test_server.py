import asyncio
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from lightweight.server import LIVE_RELOAD_JS, DevServer, LiveReloadServer


class TestServer:
    @pytest.fixture(autouse=True)
    def _create_tmp_site(self, tmp_path: Path):
        self.dir_path = tmp_path
        self.directory = str(tmp_path)
        with (tmp_path / 'file').open('w') as f:
            f.write('A test file.')
        with (tmp_path / 'index.html').open('w') as f:
            f.write('<!DOCTYPE html><html lang="en"><head><title>Test Site</title></head><body></body></html>')

    @pytest.mark.asyncio
    async def test_serves_live_reload_js(self, event_loop, unused_tcp_port):
        server = LiveReloadServer(
            self.directory,
            watch=self.directory,
            regenerate=lambda: None,
            ignored=[]
        )
        port = unused_tcp_port
        server.serve('127.0.0.1', port, loop=event_loop)

        assert 'liveReload.start();' in await get(f'http://127.0.0.1:{port}')
        assert LIVE_RELOAD_JS in await get(f'http://127.0.0.1:{port}')
        assert LIVE_RELOAD_JS in await get(f'http://127.0.0.1:{port}/index')
        assert LIVE_RELOAD_JS in await get(f'http://127.0.0.1:{port}/index.html')
        identifier = server.live_reload_id
        assert identifier in await get(f'http://127.0.0.1:{port}/__live_reload_id__')

        with (self.dir_path / 'new-file').open('w') as f:
            f.write('Test file changes')
        await asyncio.sleep(0.5)  # wait for file change to get picked up
        new_identifier = server.live_reload_id
        assert new_identifier in await get(f'http://127.0.0.1:{port}/__live_reload_id__')
        assert identifier != new_identifier

        assert 'A test file.' in await get(f'http://127.0.0.1:{port}/file')

    @pytest.mark.asyncio
    async def test_live_reload_regenerate(self, event_loop, unused_tcp_port):
        class MockRegenerate:
            called = False

            def __call__(self):
                self.called = True

        regenerate = MockRegenerate()
        server = LiveReloadServer(self.directory, watch=self.directory, regenerate=regenerate, ignored=[])
        port = unused_tcp_port
        server.serve('127.0.0.1', port, loop=event_loop)

        assert await get(f'http://127.0.0.1:{port}/__live_reload_id__')
        with (self.dir_path / 'new-file').open('w') as f:
            f.write('Test file changes')
        await asyncio.sleep(0.5)  # wait for file change to get picked up
        assert regenerate.called

    @pytest.mark.asyncio
    async def test_live_reload_ignore(self, event_loop, unused_tcp_port):
        ignored_path = self.dir_path / 'ignore'
        ignored_path.mkdir(parents=True, exist_ok=True)
        server = LiveReloadServer(
            self.directory,
            watch=self.directory,
            regenerate=lambda: None,
            ignored=[str(ignored_path)]
        )
        port = unused_tcp_port
        server.serve('127.0.0.1', port, loop=event_loop)

        identifier = server.live_reload_id
        assert identifier in await get(f'http://127.0.0.1:{port}/__live_reload_id__')
        with (ignored_path / 'ignored.txt').open('w') as f:
            f.write('Ignored file changes')
        await asyncio.sleep(0.5)  # wait for file change to get picked up
        assert identifier == server.live_reload_id  # does not change

    @pytest.mark.asyncio
    async def test_serves_no_live_reload_js(self, event_loop, unused_tcp_port):
        server = DevServer(self.directory)
        port = unused_tcp_port
        server.serve('127.0.0.1', port, loop=event_loop)

        assert LIVE_RELOAD_JS not in await get(f'http://127.0.0.1:{port}/')
        assert LIVE_RELOAD_JS not in await get(f'http://127.0.0.1:{port}/index.')
        assert LIVE_RELOAD_JS not in await get(f'http://127.0.0.1:{port}/index.html')
        assert '404' in await get(f'http://127.0.0.1:{port}/__live_reload_id__')

        assert 'A test file.' in await get(f'http://127.0.0.1:{port}/file')

    @pytest.mark.asyncio
    async def test_403(self, event_loop, unused_tcp_port):
        server = DevServer(self.directory)
        port = unused_tcp_port
        server.serve('127.0.0.1', port, loop=event_loop)

        assert '403' in await get(f'http://127.0.0.1:{port}/../..')

    @pytest.mark.asyncio
    async def test_500(self, event_loop, unused_tcp_port):
        class BadServer(DevServer):
            def handle(self, writer, request):
                raise Exception()

        server = BadServer(self.directory)
        port = unused_tcp_port
        server.serve('127.0.0.1', port, loop=event_loop)
        assert '500' in await get(f'http://127.0.0.1:{port}/../..')


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        DevServer('non-existing')


def test_file_not_a_directory():
    with pytest.raises(NotADirectoryError):
        DevServer('resources/test.html')


async def get(url_str: str) -> str:
    await asyncio.sleep(0.01)
    url = urlsplit(url_str)
    reader, writer = await asyncio.open_connection(url.hostname, url.port)

    writer.write((f"GET {url.path or '/'} HTTP/1.0\r\n"
                  f"Host: {url.hostname}\r\n"
                  f"\r\n").encode('utf8'))
    response = await reader.read()
    writer.close()
    return response.decode('utf8')
