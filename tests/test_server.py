import threading
from contextlib import contextmanager
from http.server import HTTPServer

import requests

from lightweight.server import parser, dev_server, LIVE_RELOAD_JS


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
def background_server(server: HTTPServer):
    thread = ServerThread(server)
    thread.start()
    yield
    thread.stop()


def test_serves_live_reload_js():
    server = dev_server('site', host='0.0.0.0', port=8033, enable_reload=True)
    with background_server(server):
        assert 'liveReload.start();' in requests.get('http://0.0.0.0:8033').text
        assert LIVE_RELOAD_JS in requests.get('http://0.0.0.0:8033').text
        assert LIVE_RELOAD_JS in requests.get('http://0.0.0.0:8033/index').text
        assert LIVE_RELOAD_JS in requests.get('http://0.0.0.0:8033/index.html').text
        assert server.id == requests.get('http://0.0.0.0:8033/id').text

        assert 'A test file.' in requests.get('http://0.0.0.0:8033/file').text


def test_serves_no_live_reload_js():
    server = dev_server('site', host='0.0.0.0', port=8034, enable_reload=False)
    with background_server(server):
        assert LIVE_RELOAD_JS not in requests.get('http://0.0.0.0:8034').text
        assert LIVE_RELOAD_JS not in requests.get('http://0.0.0.0:8034/index').text
        assert LIVE_RELOAD_JS not in requests.get('http://0.0.0.0:8034/index.html').text
        assert requests.get('http://0.0.0.0:8034/id').status_code == 404

        assert 'A test file.' in requests.get('http://0.0.0.0:8034/file').text
