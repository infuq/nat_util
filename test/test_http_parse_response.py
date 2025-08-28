#!/usr/bin/env python
import socket
import urllib.parse
# try to import C parser then fallback in pure python parser.
try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser


def main():

    parser = HttpParser()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    headers = None
    body = []
    message_complete = False
    try:
        s.connect(('t.infuq.com', 80))
        s.send("GET /data/static/area.json HTTP/1.1\r\nHost: t.infuq.com\r\n\r\n".encode('utf-8'))

        while True:
            data = s.recv(1024)
            if not data:
                break

            recved = len(data)
            nparsed = parser.execute(data, recved)
            assert nparsed == recved

            if parser.is_headers_complete():
                headers = parser.get_headers()

            if parser.is_partial_body():
                body.append(parser.recv_body())

            if parser.is_message_complete():
                message_complete = True
                break

        l = b''.join(body)
        print(l.decode('utf-8'))

    finally:
        s.close()

if __name__ == "__main__":
    main()

