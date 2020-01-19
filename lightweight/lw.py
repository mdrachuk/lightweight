#!/usr/bin/env python
"""
Lightweight CLI.

@example
Access CLI help via:
```bash
lw --help
```
or
```
python -m lightweight.lw --help
```

@example
Initialize project using:
```bash
lw init example_project --url https://example.org
```
Additional help:
```bash
lw init --help
```

@example
Start a server for the project
```bash
lw serve site:dev
```
Additional help:
```bash
lw serve --help
```
"""
import asyncio
import inspect
import os
import re
import sys
from argparse import ArgumentParser
from contextlib import contextmanager
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from logging import getLogger
from os import getcwd
from pathlib import Path
from random import randint, sample
from typing import Any, Optional, Callable, List

from slugify import slugify  # type: ignore

import lightweight
from lightweight import Site, jinja, directory, jinja_env, paths, Author
from lightweight.errors import InvalidCommand
from lightweight.server import DevServer, LiveReloadServer

logger = getLogger('lightweight')


class Generator:

    def __init__(self, executable_name: str, *, source: str, out: str, host: str, port: int):
        self.executable_name = executable_name
        self.source = source
        self.out = out
        self.host = host
        self.port = port

    def generate(self):
        func = self.load_executable()
        site = func(self.host, self.port)
        if not hasattr(site, 'generate') or not positional_args_count(site.generate, equals=1):
            raise InvalidCommand(f'"{self.executable_name}" did not return an instance of Site '
                                 f'with a "site.generate(out)" method.')
        return site.generate(self.out)

    def load_executable(self):
        module_name, func_name = self.executable_name.rsplit(':', maxsplit=1)
        module = load_module(module_name, self.source)
        try:
            func = getattr(module, func_name)
        except AttributeError as e:
            raise InvalidCommand(
                f'Module "{module.__name__}" ({module.__file__}) is missing method "{func_name}".') from e
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
        loader.exec_module(module)
    return module


@contextmanager
def sys_path_starting(with_: str):
    location = with_
    sys.path.insert(0, location)
    yield
    sys.path.remove(location)


def start_server(executable_name: str, *, source: str, out: str, host: str, port: int, enable_reload: bool):
    source = os.path.abspath(source)
    out = absolute_out(out, source)

    generator = Generator(executable_name, source=source, host=host, port=port, out=out)
    generator.generate()

    if not enable_reload:
        server = DevServer(out)
    else:
        server = LiveReloadServer(out, watch=source, regenerate=generator.generate, ignored=[out])

    logger.info(f'Runner: {executable_name}')
    logger.info(f'Sources: {source}')
    logger.info(f'Out: {out}')
    logger.info(f'Starting server at: "http://{host}:{port}"')
    loop = asyncio.get_event_loop()
    server.serve(host=host, port=port, loop=loop)
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info('Stopping the server.')
        loop.stop()
        sys.exit()


def absolute_out(out: Optional[str], abs_source: str) -> str:
    if out is None:
        return str(Path(abs_source) / 'out')
    return os.path.abspath(out)


class Accent(object):
    def __init__(self):
        (self.r, self.g, self.b) = self.bright_rgb()

    @staticmethod
    def bright_rgb():
        return sample([randint(120, 255),
                       randint(120, 255),
                       randint(0, 50)], 3)


def quickstart(location: str, url: str, title: Optional[str], authors: List[str]):
    path = Path(location)
    path.mkdir(parents=True, exist_ok=True)

    abs_out = os.path.abspath(path)
    if not title:
        title = Path(abs_out).name
    if not title:
        raise InvalidCommand('Missing project title')
    title_slug = slugify_title(title)

    template_location = Path(__file__).parent / 'project-template'

    with directory(template_location), custom_jinja_tags():
        site = Site(
            url=url, title=title,
            authors=[Author(name=name) for name in authors if len(name)]
        )

        [site.include(str(p), jinja(p)) for p in paths('templates/**/*.html')]
        [site.include(str(p), jinja(p)) for p in paths('*.html')]
        site.include('site.py', jinja('site.py.jinja', title_slug=title_slug))
        site.include('requirements.txt', jinja('requirements.txt', version=lightweight.__version__))
        site.include('blog')
        [site.include(str(p), jinja(p)) for p in paths('styles/**/*css') if p.name != 'attributes.scss']
        site.include('styles/attributes.scss', jinja('styles/attributes.scss', accent=Accent()))
        site.include('js')
        site.include('img')

        site.generate(abs_out)

    logger.info(f'Lightweight project initialized in: {abs_out}')


@contextmanager
def custom_jinja_tags():
    original_tags = (jinja_env.block_start_string, jinja_env.block_end_string,
                     jinja_env.variable_start_string, jinja_env.variable_end_string,
                     jinja_env.comment_start_string, jinja_env.comment_end_string)
    jinja_env.block_start_string = '{?'
    jinja_env.block_end_string = '?}'
    jinja_env.variable_start_string = '{!'
    jinja_env.variable_end_string = '!}'
    jinja_env.comment_start_string = '{//'
    jinja_env.comment_end_string = '//}'

    yield

    (jinja_env.block_start_string, jinja_env.block_end_string,
     jinja_env.variable_start_string, jinja_env.variable_end_string,
     jinja_env.comment_start_string, jinja_env.comment_end_string) = original_tags


def slugify_title(title):
    title_slug = slugify(title, separator='_')
    title_slug = re.findall('[a-z][a-z0-9_]+$', title_slug)[0]  # in code nothing can start with digits
    title_slug.replace('\'', '’')
    return title_slug


def argument_parser():
    parser = ArgumentParser(description='Lightweight -- "code over configuration" static site generator. \n'
                                        'https://drach.uk/lightweight')

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
    qs_parser = subparsers.add_parser(name='init', description='Generate Lightweight skeleton application')
    qs_parser.add_argument('location', type=str, help='the directory to initialize site generator in')
    qs_parser.add_argument('--url', type=str, help='the url of the generated site', required=True)
    qs_parser.add_argument('--title', type=str, help='the title of of the generated site')
    qs_parser.add_argument('--authors', type=str, default='', help='comma-separated list of names')
    qs_parser.set_defaults(func=lambda args: quickstart(args.location,
                                                        url=args.url,
                                                        title=args.title,
                                                        authors=args.authors.split(',')))


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
            logger.error(f'{type(error).__name__}: {str(error)}')
            exit(-1)
    else:
        parser.parse_args(['--help'])


if __name__ == '__main__':
    main()
