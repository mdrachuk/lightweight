import threading
import time
from contextlib import contextmanager
from http.server import HTTPServer
from pathlib import Path

import pytest
import requests

from lightweight.server import parser, DevSever, LIVE_RELOAD_JS, start_watchdog


def test_args():
    args = parser.parse_args(args=('dir',))
    assert args.directory == 'dir'


class ServerThread(threading.Thread):
    def __init__(self, server: HTTPServer):
        super().__init__()
        self.server = server

    def run(self):
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()


@contextmanager
def background_server(directory: str, *, host: str, port: int, enable_reload: bool):
    id_path = start_watchdog(directory) if enable_reload else None
    server = DevSever(directory, host=host, port=port, watch_id=id_path)
    thread = ServerThread(server)
    thread.start()
    yield server
    thread.stop()


class TestServer:
    @pytest.fixture(autouse=True)
    def _create_tmp_site(self, tmp_path: Path):
        self.directory = str(tmp_path)
        with (tmp_path / 'file').open('w') as f:
            f.write('A test file.')
        with (tmp_path / 'index.html').open('w') as f:
            f.write('<!DOCTYPE html><html lang="en"><head><title>Test Site</title></head><body></body></html>')

    def test_serves_live_reload_js(self):
        with background_server(self.directory, host='0.0.0.0', port=8033, enable_reload=True) as server:
            assert 'liveReload.start();' in requests.get('http://0.0.0.0:8033').text
            assert LIVE_RELOAD_JS in requests.get('http://0.0.0.0:8033').text
            assert LIVE_RELOAD_JS in requests.get('http://0.0.0.0:8033/index').text
            assert LIVE_RELOAD_JS in requests.get('http://0.0.0.0:8033/index.html').text
            with open(server.id_path) as idfile:
                identifier = idfile.read()
            assert identifier == requests.get('http://0.0.0.0:8033/id').text
            with (Path(self.directory) / 'new-file').open('w') as f:
                f.write('Test file changes')
            time.sleep(1)
            with open(server.id_path) as idfile:
                new_identifier = idfile.read()
            assert new_identifier == requests.get('http://0.0.0.0:8033/id').text
            assert identifier != new_identifier

            assert 'A test file.' in requests.get('http://0.0.0.0:8033/file').text

    def test_serves_no_live_reload_js(self):
        with background_server(self.directory, host='0.0.0.0', port=8034, enable_reload=False):
            assert LIVE_RELOAD_JS not in requests.get('http://0.0.0.0:8034').text
            assert LIVE_RELOAD_JS not in requests.get('http://0.0.0.0:8034/index').text
            assert LIVE_RELOAD_JS not in requests.get('http://0.0.0.0:8034/index.html').text
            assert requests.get('http://0.0.0.0:8034/id').status_code == 404

            assert 'A test file.' in requests.get('http://0.0.0.0:8034/file').text


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        DevSever('non-existing', host='0.0.0.0', port=8080, watch_id=None)


def test_file_not_a_directory():
    with pytest.raises(NotADirectoryError):
        DevSever('resources/test.html', host='0.0.0.0', port=8080, watch_id=None)
