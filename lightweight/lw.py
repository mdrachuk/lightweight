#!/usr/bin/env python
import asyncio
import inspect
import os
import sys
from argparse import ArgumentParser
from contextlib import contextmanager
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from os import getcwd
from pathlib import Path
from typing import Any, Optional, Callable

import lightweight
from lightweight.errors import InvalidCommand
from lightweight.server import DevServer, LiveReloadServer, RunGenerate


def get_generator(executable_name: str, *, source: str, out: str, host: str, port: int) -> RunGenerate:
    func = get_executable(source, executable_name)

    def generate():
        site = func(host, port)
        if not hasattr(site, 'generate') or not positional_args_count(site.generate, equals=1):
            raise InvalidCommand(f'"{executable_name}" did not return an instance of Site '
                                 f'with a "site.generate(out)" method.')
        return site.generate(out)

    return generate


def get_executable(module_location, path):
    module_name, func_name = path.rsplit(':', maxsplit=1)
    module = load_module(module_name, module_location)
    try:
        func = getattr(module, func_name)
    except AttributeError as e:
        raise InvalidCommand(f'Module "{module.__name__}" ({module.__file__}) is missing method "{func_name}".') from e
    if not callable(func):
        raise InvalidCommand(f'"{module.__name__}:{func_name}" member is not callable.')
    if not positional_args_count(func, equals=2):
        raise InvalidCommand(f'"{module.__name__}:{func_name}" cannot be called as "{func_name}(host, port)".')
    return func


def positional_args_count(func: Callable, *, equals: int):
    """
    @example
    if not positional_args_count(func, equals=2):
        ...
    """
    count = equals
    params = inspect.signature(func).parameters
    return len(params) >= count and all(p.default != p.empty for p in list(params.values())[count:])


def load_module(module_name: str, module_location: str) -> Any:
    module_file_path = os.path.join(f'{module_location}', f'{module_name}.py')
    with sys_path_starting(with_=module_location):
        loader = SourceFileLoader(module_name, module_file_path)
        spec = spec_from_loader(module_name, loader, is_package=False)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


@contextmanager
def sys_path_starting(with_: str):
    location = with_
    os.sys.path.insert(0, location)
    yield
    os.sys.path.remove(location)


def start_server(executable_name: str, *, source: str, out: str, host: str, port: int, enable_reload: bool):
    source_path = Path(source)
    source = str(source_path.absolute())
    out = absolute_out(out, source_path)

    generate = get_generator(executable_name, source=source, host=host, port=port, out=out)

    if enable_reload:
        server = LiveReloadServer(out, watch=source, regenerate=generate, ignored=[out])
    else:
        server = DevServer(out)

    generate()

    print(
        f'Server for "{executable_name}" at "{source}" is starting at "http://{host}:{port}".\n'
        f'Out directory: {out}'
    )
    loop = asyncio.get_event_loop()
    server.serve(host=host, port=port, loop=loop)
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        print('Stopping the server.')
        loop.stop()
        sys.exit()


def absolute_out(out: Optional[str], source_path: Path) -> str:
    out_path = source_path / 'out' if out is None else Path(out)
    return str(out_path.absolute())


def quickstart(directory):
    pass


def argument_parser():
    parser = ArgumentParser(description='Lightweight CLI')

    subparsers = parser.add_subparsers()

    add_server_cli(subparsers)
    add_init_cli(subparsers)
    add_version_cli(subparsers)

    return parser


def add_server_cli(subparsers):
    server_parser = subparsers.add_parser(name='serve', description='Lightweight development server for static files')
    server_parser.add_argument('executable', type=str,
                               help='Function accepting a host and a port and returning a Site instance '
                                    'specified as "<module>:<function>" '
                                    '(e.g. "site:dev" to call "dev(host, port)" method of "site.py")')
    server_parser.add_argument('--source', type=str, default=getcwd(),
                               help='project location: parent directory of a "generator". Defaults to cwd.')
    server_parser.add_argument('--out', type=str, default=None, help='output directory for generation results.'
                                                                     'Defaults to project directory')
    server_parser.add_argument('--host', type=str, default='localhost', help='defaults to "localhost"')
    server_parser.add_argument('--port', type=int, default=8080, help='defaults to "8080"')
    server_parser.add_argument('--no-live-reload', action='store_true', default=False,
                               help='disable live reloading '
                                    '(enabled by default calling the executable on every project file change)')
    server_parser.set_defaults(func=lambda args: start_server(args.executable,
                                                              source=args.source,
                                                              out=args.out,
                                                              host=args.host,
                                                              port=args.port,
                                                              enable_reload=not args.no_live_reload))


def add_init_cli(subparsers):
    qs_parser = subparsers.add_parser(name='init', description='Generate Lightweight quickstart application')
    qs_parser.add_argument('location', type=str, help='the directory to generate application')
    qs_parser.set_defaults(func=lambda args: quickstart(args.directory))


def add_version_cli(subparsers):
    version_parser = subparsers.add_parser(name='version')
    version_parser.set_defaults(func=lambda args: print(lightweight.__version__))


def main():
    parser = argument_parser()
    args = parser.parse_args()
    if hasattr(args, 'func'):
        try:
            args.func(args)
        except InvalidCommand as error:
            print(f'{type(error).__name__}: {str(error)}', file=sys.stderr)
            exit(-1)
    else:
        parser.parse_args(['--help'])


if __name__ == '__main__':
    main()
