# Mostly stolen from picoweb web pico-framework for Pycopy 2019 MIT

from __future__ import annotations

import os
from asyncio import StreamReader, StreamWriter, start_server
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from logging import getLogger
from pathlib import Path
from typing import Dict, Collection, Callable
from uuid import uuid4

from watchgod import awatch  # type: ignore

logger = getLogger('lightweight')


@dataclass(frozen=True)
class HttpRequest:
    """A request processed by the server."""
    headers: Dict[str, str]
    reader: StreamReader
    qs: str
    location: str
    method: str


@dataclass(frozen=True)
class File:
    """A file that is served via HTTP."""
    path: Path
    mime_type: MimeType

    def read(self) -> bytes:
        with self.path.open('rb') as f:
            return f.read()


class MimeType(Enum):
    """Mime-type of the file written to response Content-Type."""
    html = 'text/html'
    css = 'text/css'
    image = 'image'
    plaintext = 'text/plain'

    @classmethod
    def of(cls, path: Path) -> MimeType:
        if path.suffix == '.html':
            return cls.html
        if path.suffix == '.css':
            return cls.css
        if path.suffix == '.png' or path.suffix == '.jpg' or path.suffix == '.jpeg' or path.suffix == '.gif':
            return cls.image
        return cls.plaintext


def u(string: str) -> bytes:
    """Shortcut to encode string to bytes."""
    return string.encode('utf8')


class DevServer:
    """A server serving static files from the provided directory.

    @example
    ```python
    server = DevServer('app/static')
    loop = asyncio.get_event_loop()
    loop.create_task(server.serve('localhost', 8080))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
    ```
    """

    def __init__(self, location: str):
        self.working_dir = Path(os.path.abspath(location))
        check_directory(self.working_dir)

    def serve(self, host, port, loop):
        """Creates an asyncio coroutine, that serves requests on the provided host and port.

        @example
        ```python
        loop = asyncio.get_event_loop()
        loop.create_task(server.serve('localhost', 8080))
        loop.run_forever()
        ```
        """
        loop.create_task(start_server(self.respond, host, port))

    def handle(self, writer: StreamWriter, request: HttpRequest):
        """Handle the request and write the response."""
        return self.handle_static(writer, request)

    def handle_static(self, writer: StreamWriter, request: HttpRequest):
        """Look for file and write it to the writer.
        In case the file not found or there are other problems -- write an error.
        """
        try:
            file = self.find_file(request.location[1:])
            return self.sendfile(writer, file)
        except PermissionError:
            return self.http_error(writer, '403')
        except FileNotFoundError:
            return self.http_error(writer, '404')

    def find_file(self, location: str) -> File:
        """Override to change how path is resolved to file."""
        # TODO:mdrachuk:10.01.2020: read file asynchronously
        exact = self.working_dir / location
        html = self.working_dir / f'{location}.html'
        index = self.working_dir / location / 'index.html'
        if not os.path.abspath(exact).startswith(str(self.working_dir)):
            raise PermissionError()
        if exact.exists() and not exact.is_dir():
            path = exact
        elif html.exists() and not html.is_dir():
            path = html
        elif index.exists() and not index.is_dir():
            path = index
        else:
            raise FileNotFoundError()
        return File(path=path, mime_type=MimeType.of(path))

    def sendfile(self, writer: StreamWriter, file: File):
        """Override to response with file is put together."""
        self.start_response(writer, file.mime_type.value, '200')
        writer.write(file.read())

    @staticmethod
    def start_response(writer: StreamWriter,
                       content_type: str = "text/html; charset=utf-8",
                       status: str = "200",
                       headers: Dict[str, str] = None):
        writer.write(u(f'HTTP/1.0 {status} NA\r\n'))
        writer.write(u(f'Content-Type: {content_type}'))
        if headers:
            writer.write(u('\r\n'))
            for k, v in headers.items():
                writer.write(u(f'{k}: {v}'))
        writer.write(u('\r\n\r\n'))

    @classmethod
    def http_error(cls, writer: StreamWriter, status: str):
        cls.start_response(writer, status=status)
        writer.write(u(status))

    async def respond(self, reader: StreamReader, writer: StreamWriter):
        first_line = await reader.readline()
        method: str
        path: str
        proto: str
        method, path, proto = first_line.decode().split()
        logger.info(f'{now_repr()}: {method} {path} Requested')
        try:
            if '?' in path:
                path, qs = path.split('?', 1)
            else:
                qs = ''
            headers = await self._parse_headers(reader)
            request = HttpRequest(
                method=method,
                location=path,
                headers=headers,
                qs=qs,
                reader=reader,
            )
            self.handle(writer, request)
        except Exception:
            self.http_error(writer, '500')
            raise
        finally:
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            logger.info(f'{now_repr()}: {method} {path} Done')

    @staticmethod
    async def _parse_headers(reader: StreamReader):
        headers = {}
        while True:
            line = await reader.readline()
            if line == b'\r\n':
                break
            k, v = line.split(b':', 1)
            headers[k] = v.strip()
        return headers


def check_directory(working_dir: Path):
    if not working_dir.exists():
        raise FileNotFoundError(f'Directory {working_dir} does not exist')
    if not working_dir.is_dir():
        raise NotADirectoryError(f'{working_dir} is not a directory')
    return working_dir


RunGenerate = Callable[[], None]


class LiveReloadServer(DevServer):
    def __init__(
            self,
            location: str,
            *,
            watch: str,
            regenerate: RunGenerate,
            ignored: Collection[str] = tuple()
    ):
        super().__init__(location)
        self.live_reload_id = self._new_id()
        self.watch_location = os.path.abspath(watch)
        self.regenerate = regenerate
        self.ignored = ignored

    def serve(self, host, port, loop):
        super().serve(host, port, loop)
        loop.create_task(self.watch_source())

    def handle(self, writer: StreamWriter, request: HttpRequest):
        if request.location == '/__live_reload_id__':
            return self.send_live_reload_id(writer)
        else:
            return self.handle_static(writer, request)

    def sendfile(self, writer: StreamWriter, file: File):
        if file.mime_type == MimeType.html:
            self.start_response(writer, file.mime_type.value, '200')
            writer.write(u(
                file.read()
                    .decode('utf8')
                    .replace('</body>', f'{LIVE_RELOAD_JS}</body>')
            ))
        else:
            super().sendfile(writer, file)

    def send_live_reload_id(self, writer: StreamWriter):
        self.start_response(writer)
        writer.write(u(self.live_reload_id))

    async def watch_source(self):
        async for changes in awatch(str(self.watch_location)):
            for change, location in changes:
                if len(self.ignored) and all(location.startswith(path) for path in self.ignored):
                    continue
                self.on_source_changed()
                break

    def on_source_changed(self):
        logger.info('Source change. Live reload triggered.')
        self.live_reload_id = self._new_id()
        try:
            self.regenerate()
        except Exception as e:
            logger.exception('Exception when generating the site: ', exc_info=e)

    @staticmethod
    def _new_id():
        return str(uuid4())


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
        return fetch('/__live_reload_id__').then(data => data.text());
    }

    function reloadOnChange(currentId) {
        stopped = false;
        interval = setInterval(check, 1000);

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


def now_repr():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
