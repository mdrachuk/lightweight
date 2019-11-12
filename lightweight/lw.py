#!/usr/bin/env python
from argparse import ArgumentParser

from lightweight.server import DevSever, start_watchdog


def start_server(directory: str, *, host: str, port: int, enable_reload: bool):
    id_path = start_watchdog(directory) if enable_reload else None
    server = DevSever(directory, host=host, port=port, watch_id=id_path)
    print(f'Server for "{directory}" starting at "{host}:{port}"')
    server.serve_forever()


def quickstart(directory):
    pass


parser = ArgumentParser(description='Lightweight CLI')

subparsers = parser.add_subparsers()

server_parser = subparsers.add_parser(name='server', description='Lightweight development server for static files')
server_parser.add_argument('directory', type=str, help='the directory to serve files from')
server_parser.add_argument('--host', type=str, default='0.0.0.0')
server_parser.add_argument('--port', type=int, default=8080)
server_parser.add_argument('--no-live-reload', action='store_true', default=False, help='disable live reloading')
server_parser.set_defaults(func=lambda args: start_server(args.directory,
                                                          host=args.host,
                                                          port=args.port,
                                                          enable_reload=not args.no_live_reload))

qs_parser = subparsers.add_parser(name='quickstart', description='Generate Lightweight quickstart application')
qs_parser.add_argument('directory', type=str, help='the directory to generate application')
qs_parser.set_defaults(func=lambda args: quickstart(args.directory))

if __name__ == '__main__':
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.parse_args(['--help'])
