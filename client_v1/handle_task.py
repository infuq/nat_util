import json

from client_v1.connect_server_socket import connect_proxied_socket
from codec.http_codec import http_decode_response
from codec.nat_codec import nat_encode
from common.const import PROXY_HTTP_REQUEST_TO_PROXIED_SERVER_TASK, NAT_COMMAND_RESPONSE

PROXY_HTTP_RESPONSE_TO_NAT_SERVER_TASK_LIST = []
PROXY_HTTP_REQUEST_TO_PROXIED_SERVER_TASK_LIST = []
try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser


def run_all_tasks(nat_socket, proxied_host, proxied_port):
    if len(PROXY_HTTP_REQUEST_TO_PROXIED_SERVER_TASK_LIST) < 1:
        return

    for task in PROXY_HTTP_REQUEST_TO_PROXIED_SERVER_TASK_LIST:
        command = task['command']
        data = task['data']
        if command == PROXY_HTTP_REQUEST_TO_PROXIED_SERVER_TASK:
            """ data = 
            {
                "method": "POST",
                "url": "/data/check/success",
                "headers": {
                    "Host": "192.168.10.13:38081",
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept": "*/*",
                    "Connection": "keep-alive",
                    "Content-Length": "48"
                },
                "body": {
                    "keyword": "红薯",
                    "k": "白糖"
                },
                "conn_proxy_socket_fd": 328
            }
            """

            method = data['method']
            url = data['url']
            headers = data['headers']
            body = data['body']
            conn_proxy_socket_fd = data['conn_proxy_socket_fd']

            # 1.连接真正的被代理服务
            proxied_socket = connect_proxied_socket(
                host=proxied_host,
                port=proxied_port,
                blocking=True
            )

            # 2.构造HTTP请求体
            http_frame = []
            http_frame.append(f'{method} {url} HTTP/1.1\r\n')

            for header in headers:
                if header == 'Host':
                    http_frame.append(f'{header}: {proxied_host}:{proxied_port}\r\n')
                else:
                    http_frame.append(f'{header}: {headers[header]}\r\n')
            http_frame.append('\r\n')
            if body is not None:
                http_frame.append(body)

            request = "".join(http_frame)
            # 3.发送HTTP请求
            proxied_socket.sendall(bytes(request.encode('utf-8')))

            # 4.解析响应
            response = http_decode_response(proxied_socket, HttpParser())

            response['conn_proxy_socket_fd'] = conn_proxy_socket_fd

            print(f'将客户端的HTTP请求响应转发给NAT Server, data={json.dumps(response)}')
            nat_frame = nat_encode(response, NAT_COMMAND_RESPONSE)
            # 5.将HTTP响应内容转发给 NAT Server
            nat_socket.sendall(nat_frame)

    PROXY_HTTP_REQUEST_TO_PROXIED_SERVER_TASK_LIST.clear()

