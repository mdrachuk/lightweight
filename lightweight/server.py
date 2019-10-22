from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum, auto
from http.server import HTTPServer, BaseHTTPRequestHandler
from mimetypes import types_map
from pathlib import Path
from uuid import uuid4


class FileType(Enum):
    exact = auto()
    html = auto()
    index = auto()


@dataclass
class File:
    path: Path
    content: bytes
    type: FileType


class StaticFiles(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            file = self.file()
            self.send_response(200)
            mime_type = types_map.get(file.path.suffix, None)
            self.send_header('Content-type', mime_type)
            self.end_headers()
            body = self.response_body(file)
            self.wfile.write(body)
        except IOError:
            self.send_error(404, f'File Not Found: {self.path}')

    def response_body(self, file: File) -> bytes:
        return file.content

    def file(self) -> File:
        location = self.path[1:] if self.path.startswith('/') else self.path
        working_dir: Path = self.server.working_dir  # type: ignore
        exact = working_dir / location
        html = working_dir / f'{location}.html'
        index = working_dir / location / 'index.html'
        if exact.exists() and not exact.is_dir():
            file_type = FileType.exact
            path = exact
        elif html.exists() and not html.is_dir():
            file_type = FileType.html
            path = html
        elif index.exists() and not index.is_dir():
            file_type = FileType.index
            path = index
        else:
            raise FileNotFoundError()

        with path.open('rb') as f:
            return File(path, f.read(), file_type)


class LiveStaticFiles(StaticFiles):
    def do_GET(self):
        if self.path == '/id':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(self.server.id.encode('utf8'))
        else:
            super().do_GET()

    def response_body(self, file: File) -> bytes:
        if file.path.suffix == '.html':
            return (file.content
                    .decode('utf8')
                    .replace('</body>', f'{LIVE_RELOAD_JS}</body>')
                    .encode('utf8'))
        return file.content


def dev_server(directory: str, *, host: str, port: int, enable_reload: bool) -> HTTPServer:
    working_dir = Path(directory).resolve()
    check_directory(working_dir)
    address = (host, port)
    handler = LiveStaticFiles if enable_reload else StaticFiles
    server = HTTPServer(address, handler)
    server.working_dir = working_dir  # type: ignore
    server.id = str(uuid4())  # type: ignore
    return server


def check_directory(working_dir: Path):
    if not working_dir.exists():
        raise FileNotFoundError(f'Directory {working_dir} does not exist')
    if not working_dir.is_dir():
        raise NotADirectoryError(f'{working_dir} is not a directory')
    return working_dir


LIVE_RELOAD_JS = """
<!-- Script injected by the Lightweight Dev Server to reload in case of changes. -->
<script type="application/javascript">
const liveReload = function f() {
    let interval = null;
    let stopped = null;

    return {
        start: () => fetchId().then(reloadOnChange),
        stop: () => stop(),
    };

    function fetchId() {
        return fetch('/id').then(data => data.text());
    }

    function reloadOnChange(currentId) {
        stopped = false;
        interval = setInterval(check, 500);

        function check() {
            fetchId().then(newId => {
                if (!stopped && newId !== currentId) {
                    location.reload()
                }
            });
        }
    }

    function stop() {
        clearInterval(interval);
        stopped = false;
    }
}();
liveReload.start();
</script>
"""

parser = ArgumentParser(description='Lightweight development server for static files')
parser.add_argument('directory', type=str, help='the directory to serve files from')

parser.add_argument('--host', type=str, default='0.0.0.0')
parser.add_argument('--port', type=int, default=8080)
parser.add_argument('--no-live-reload', action='store_true', default=False, help='disable live reloading')

if __name__ == '__main__':
    args = parser.parse_args()
    server = dev_server(args.directory,
                        host=args.host,
                        port=args.port,
                        enable_reload=not args.no_live_reload)
    server.serve_forever()
