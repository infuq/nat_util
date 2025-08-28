#!/usr/bin/env python
import socket
import json
import urllib.parse

# try to import C parser then fallback in pure python parser.
try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser


def main():

    parser = HttpParser()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind(('127.0.0.1', 8081))
    server.listen(5)
    print('Server start success...')
    client, addr = server.accept()
    print(f'Server accept client\'addr {addr}')
    request_headers = None
    body = []
    try:

        while True:
            data = client.recv(1024)
            if not data:
                break

            recved = len(data)
            nparsed = parser.execute(data, recved)
            assert nparsed == recved

            if parser.is_headers_complete():
                request_headers = parser.get_headers()

            if parser.is_partial_body():
                body.append(parser.recv_body())

            if parser.is_message_complete():
                break

        headers = {}
        for key in request_headers:
            value = request_headers[key]
            headers[key] = value
            if key == 'Host':
                port = value.split(':')[-1]
                headers['ip'] = value.split(':')[0]
                headers['port'] = port

        print('headers', headers)
        print('method', parser.get_method())
        print('path', parser.get_path())
        print('url', urllib.parse.unquote(parser.get_url()))
        print('query_string', urllib.parse.unquote(parser.get_query_string()))
        print('status_code', parser.get_status_code())
        print('version', parser.get_version())

        l = b''.join(body)
        print(json.loads(l.decode('utf-8')))


    finally:
        client.close()
        server.close()

if __name__ == "__main__":
    main()

