#!/usr/bin/env python
import asyncio
import os
from argparse import ArgumentParser
from contextlib import contextmanager
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from os import getcwd
from pathlib import Path

from lightweight.server import DevServer, LiveReloadServer


def get_generator(path: str, *, module_location: str, source: str, out: str):
    module_name, func_name = path.rsplit(':', maxsplit=1)
    module_file_path = os.path.join(f'{module_location}', f'{module_name}.py')
    with sys_path_starting(with_=module_location):
        loader = SourceFileLoader(module_name, module_file_path)
        spec = spec_from_loader(module_name, loader, is_package=False)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
    func = getattr(module, func_name)
    return lambda: func(source, out)


@contextmanager
def sys_path_starting(with_: str):
    location = with_
    os.sys.path.insert(0, location)
    yield
    os.sys.path.remove(location)


def start_server(generator_name: str, *, source: str, out: str, host: str, port: int, enable_reload: bool):
    source = str(Path(source).absolute())
    if out is None:
        out = str((Path(source) / 'out').absolute())
    else:
        out = str(Path(out).absolute())
    generate = get_generator(generator_name, module_location=source, source=source, out=out)

    if enable_reload:
        server = LiveReloadServer(out, watch=source, regenerate=generate, ignored=[out])
    else:
        server = DevServer(out)

    generate()

    print(
        f'Server for "{generator_name}" at "{source}" is starting at "http://{host}:{port}".\n'
        f'Out directory: {out}'
    )
    try:
        loop = asyncio.get_event_loop()
        print('Source', source)
        server.serve(host=host, port=port, loop=loop)
        loop.run_forever()
    except KeyboardInterrupt:
        pass  # TODO:mdrachuk:12.01.2020: shutdown


def quickstart(directory):
    pass


def argument_parser():
    parser = ArgumentParser(description='Lightweight CLI')

    subparsers = parser.add_subparsers()

    server_parser = subparsers.add_parser(name='serve', description='Lightweight development server for static files')
    server_parser.add_argument('generator', type=str,
                               help='reference of a function called to generate a site '
                                    '(e.g. pass "site.dev" to call "dev(...)" method of "site.py")')
    server_parser.add_argument('--source', type=str, default=getcwd(),
                               help='project location: parent directory of a "generator". Defaults to cwd.')
    server_parser.add_argument('--out', type=str, default=None, help='output directory for generation results.'
                                                                     'Defaults to project direc')
    server_parser.add_argument('--host', type=str, default='127.0.0.1', help='defaults to "127.0.0.1"')
    server_parser.add_argument('--port', type=int, default=8080, help='defaults to "8080"')
    server_parser.add_argument('--no-live-reload', action='store_true', default=False,
                               help='disable live reloading '
                                    '(enabled by default calling the generator on every project file change)')
    server_parser.set_defaults(func=lambda args: start_server(args.generator,
                                                              source=args.source,
                                                              out=args.out,
                                                              host=args.host,
                                                              port=args.port,
                                                              enable_reload=not args.no_live_reload))

    qs_parser = subparsers.add_parser(name='init', description='Generate Lightweight quickstart application')
    qs_parser.add_argument('location', type=str, help='the directory to generate application')
    qs_parser.set_defaults(func=lambda args: quickstart(args.directory))
    return parser


def main():
    parser = argument_parser()
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.parse_args(['--help'])


if __name__ == '__main__':
    main()
