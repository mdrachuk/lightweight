"""
A simple CLI for lightweight projects:
```python
# website.py

def dev(host: str, port: int) -> Site:
    site = Site(url=f'http://{host}:{port}/', title='HOME')
    ...
    return site

if __name__ == '__main__':
    cli = SiteCli(build=dev, default_port=8081)
    cli.run()
```

This allows to build the project: `./website.py build --url https://lightweight.site/`;
and to run the dev server: `./website.py serve --port 8069`
"""

import inspect
from argparse import ArgumentParser
from logging import getLogger
from os import getcwd
from pathlib import Path
from typing import Callable, Any

from .errors import InvalidCommand
from .lw import start_server, FailedGeneration
from .site import Site

logger = getLogger('lightweight')


class SiteCli:
    def __init__(
            self,
            build: Callable[[str], Site],
            *,
            default_host: str = 'localhost',
            default_port: int = 8080,
            default_out: str = None
    ):
        """
        @param build: a module level function that receives the site’s URL `str` and returns a collected [Site]
        @param default_host: a string used as host when it’s not provided to CLI
        @param default_port: an in used as port when it’s not provided to CLI
        @param default_out: a directory site is outputted to; defaults to "{cwd}/out"
        """
        self.build = build
        self.default_host = default_host
        self.default_port = default_port
        self.default_out = default_out if default_out is not None else Path(getcwd()) / 'out'

    def run(self):
        args = self._argument_parser().parse_args()
        if hasattr(args, 'func'):
            args.func(args)
        else:
            self.help()

    def help(self):
        self._argument_parser() \
            .parse_args(['--help'])

    def _argument_parser(self):
        parser = ArgumentParser(description="https://drach.uk/ -- lightweight static site")
        self._add_commands(parser.add_subparsers())
        return parser

    def _add_commands(self, subparsers):
        self._add_build_cli(subparsers)
        self._add_server_cli(subparsers)

    def _add_build_cli(self, subparsers):
        p = subparsers.add_parser(name='build', description='')
        p.add_argument('--out', type=str, default=self.default_out,
                       help='output directory for generation results.Defaults to cwd / "out"')
        p.add_argument('--host', type=str, default=None, help=f'defaults to "{self.default_host}"')
        p.add_argument('--port', type=int, default=None, help=f'defaults to "{self.default_port}"')
        p.add_argument('--url', type=str, default=None,
                       help=f'defaults to "http://{self.default_host}:{self.default_port}/"')
        p.set_defaults(func=self._run_build)

    def _run_build(self, args: Any):
        url: str
        if args.url is not None:
            if args.host is not None or args.port is not None:
                raise InvalidCommand("Can’t combine --url with --host and --port.")
            url = args.url
        else:
            host = args.host if args.host is not None else self.default_host
            port = args.port if args.port is not None else self.default_port
            url = f'http://{host}:{port}/'
        self.build(url).generate(args.out)

    def _add_server_cli(self, subparsers):
        p = subparsers.add_parser(name='serve',
                                  description='Lightweight development server for static files')
        p.add_argument('--watch', type=str, default=getcwd(),
                       help='project location: parent directory of a "generator". Defaults to cwd.')
        p.add_argument('--out', type=str, default=self.default_out,
                       help='output directory for generation results.Defaults to cwd / "out"')
        p.add_argument('--host', type=str, default=self.default_host,
                       help=f'defaults to "{self.default_host}"')
        p.add_argument('--port', type=int, default=self.default_port,
                       help=f'defaults to "{self.default_port}"')
        p.add_argument('--no-live-reload', action='store_true', default=False,
                       help='disable live reloading '
                            '(enabled by default calling the executable on every project file change)')
        func_file_path = Path(inspect.getsourcefile(self.build))
        func_name = self.build.__qualname__
        p.set_defaults(func=lambda args: self._run_serve(func_file_path, func_name, args))

    def _run_serve(self, func_file: Path, func_name: str, args: Any):
        try:
            start_server(
                func_file,
                func_name,
                source=args.watch,
                out=args.out,
                host=args.host,
                port=args.port,
                enable_reload=not args.no_live_reload,
            )
        except FailedGeneration as e:
            pass
