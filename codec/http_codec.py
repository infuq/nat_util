import urllib.parse
import urllib.parse
import json
from common.const import *

"""
1.外网的 Client 与 NAT Server 通信
2.内网的 NAT Client 与 内网服务 通信
"""

# HTTP请求解码器
def http_decode_request(conn_socket, parser):
    request_headers = None
    body = []
    message_complete = False
    while True:
        data = conn_socket.recv(RECV_MAX_SIZE)
        if not data:
            if parser.is_message_complete() and len(body) == 0:
                return NEED_CLOSE_CONN
            else:
                break

        recved = len(data)
        nparsed = parser.execute(data, recved)
        assert nparsed == recved

        if parser.is_headers_complete():
            request_headers = parser.get_headers()

        if parser.is_partial_body():
            body.append(parser.recv_body())

        if parser.is_message_complete():
            message_complete = True
            break
    if not message_complete:
        return NOT_FULL_FRAME

    port = None
    headers = {}
    for key in request_headers:
        value = request_headers[key]
        headers[key] = value
        if key == 'Host':
            port = int(value.split(':')[-1])
            headers['port'] = port

    method          = parser.get_method()
    path            = parser.get_path()
    url             = urllib.parse.unquote(parser.get_url())
    query_string    = urllib.parse.unquote(parser.get_query_string())

    body_obj = None
    if len(body) > 0: # 需要再判断 Content-Type ?
        l = b''.join(body)
        body_obj = json.loads(l.decode('utf-8'))

    return {
        "port": port,
        "method": method,
        "url": url,
        "headers": headers,
        "body": body_obj
    }


# HTTP响应解码器
def http_decode_response(conn_socket, parser):
    request_headers = None
    body_l = []
    message_complete = False
    while True:
        data = conn_socket.recv(RECV_MAX_SIZE)
        if not data:
            break

        recved = len(data)
        nparsed = parser.execute(data, recved)
        assert nparsed == recved

        if parser.is_headers_complete():
            request_headers = parser.get_headers()

        if parser.is_partial_body():
            body_l.append(parser.recv_body())

        if parser.is_message_complete():
            message_complete = True
            break
    if not message_complete:
        return NOT_FULL_FRAME


    headers = {}
    for key in request_headers:
        value = request_headers[key]
        headers[key] = value

    body = None
    if len(body_l) > 0:  # 需要再判断 Content-Type ?
        l = b''.join(body_l)
        body = l.decode('utf-8')

    return {
        "headers": headers,
        "body": body
    }
