import argparse
import json
import re

import select

from client_v1.connect_server_socket import *
from client_v1.handle_nat_server_request import handle_nat_server_request
from client_v1.handle_proxied_response import handle_proxied_response
from close_conn_socket import *
from codec.http_codec import http_decode_response
from codec.nat_codec import nat_encode
from common.const import *

try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser

def __init():
    parser = argparse.ArgumentParser(description="NAT Client")
    # parser.add_argument(
    #     "--proxy_protocol", help="Protocol of connection", required=True
    # )
    parser.add_argument(
        "--nat_server_host", help="Nat Server Host", required=True
    )
    parser.add_argument(
        "--nat_server_port", type=int, help="Nat Server Port", required=True
    )
    parser.add_argument(
        "--proxy_port", type=str, help="Proxy Port", required=True
    )
    parser.add_argument(
        "--proxied_host", type=str, help="Proxied Host", required=True
    )
    parser.add_argument(
        "--proxied_port", type=int, help="Proxied Port", required=True
    )

    args = parser.parse_args()

    nat_server_host = args.nat_server_host
    nat_server_port = args.nat_server_port
    nat_server_port = int(nat_server_port)

    # 连接 NAT Server
    nat_socket = connect_nat_server(host=nat_server_host, port=nat_server_port)

    data = {
        "proxy_protocol": 'HTTP', # 目前仅支持HTTP协议
        "proxy_port": int(args.proxy_port) # 委托 NAT Server 监听 proxy_port, 一旦该端口有客户端连接, 将其请求数据转发到 NAT Client
    }
    frame = nat_encode(data, NAT_COMMAND_PROXY)
    nat_socket.sendall(frame)

    conn_nat_socket_list.append(nat_socket)
    conn_nat_socket_fd_map[nat_socket.fileno()] = {
        NAT_PARSER_REQUEST: EMPTY_MERGE_CUMULATOR,
        SOCKET_KEY: nat_socket
    }

    # 连接被代理服务
    # proxied_socket = connect_proxied_socket(
    #     host=args.proxied_host,
    #     port=args.proxied_port
    # )
    # conn_proxied_socket_list.append(proxied_socket)
    # conn_proxied_socket_fd_map[proxied_socket.fileno()] = {
    #     HTTP_PARSER_RESPONSE: HttpParser(),
    #     SOCKET_KEY: proxied_socket
    # }

    return nat_socket, args.proxied_host, args.proxied_port


def __process_task(nat_socket, proxied_host, proxied_port, TASK_PROXY_HTTP_REQUEST_TO_PROXIED_SERVER_LIST, TASK_PROXY_HTTP_RESPONSE_TO_NAT_SERVER_LIST):

    for task in TASK_PROXY_HTTP_REQUEST_TO_PROXIED_SERVER_LIST:
        command = task['command']
        data = task['data']
        if command == TASK_PROXY_HTTP_REQUEST_TO_PROXIED_SERVER:
            print('将客户端发送来的请求转发给内网服务')
            conn_proxy_socket_fd = data['conn_proxy_socket_fd']
            port = data['port']
            method = data['method']
            url = data['url']
            headers = data['headers']
            body = data['body']

            print('\t连接被代理服务')
            proxied_socket = connect_proxied_socket(
                host=proxied_host,
                port=proxied_port,
                blocking=True
            )

            http_frame = []
            http_frame.append(f'{method} {url} HTTP/1.1\r\n')

            for header in headers:
                if header == 'Host':
                    http_frame.append(f'{header}: {proxied_host}:{proxied_port}\r\n')
                else:
                    http_frame.append(f'{header}: {headers[header]}\r\n')
            http_frame.append('\r\n')
            if body is not None:
                http_frame.append(json.dumps(body))

            print(f'\t向被代理服务发送数据, data: {http_frame}')
            request = "".join(http_frame)
            proxied_socket.sendall(bytes(request.encode('utf-8')))

            # 响应
            response = http_decode_response(proxied_socket, HttpParser())
            print(f'\t接收被代理服务响应内容, data: {json.dumps(response)}')

            response['conn_proxy_socket_fd'] = conn_proxy_socket_fd

            print(f'将客户端发送来的请求响应转发给NAT Server. data: {json.dumps(response)}')
            nat_frame = nat_encode(response, NAT_COMMAND_RESPONSE)
            nat_socket.sendall(nat_frame)

    TASK_PROXY_HTTP_REQUEST_TO_PROXIED_SERVER_LIST.clear()


def main_loop():
    nat_socket, proxied_host, proxied_port = __init()

    while True:
        try:

            read_socket_list = [
                sock
                for sock in (conn_nat_socket_list + conn_proxied_socket_list)
                if sock.fileno() != -1
            ]

            # 轮询IO事件
            readable, writable, errored = select.select(read_socket_list, [], [], 0.5)

            # 处理IO事件
            for sock in readable:
                if sock in conn_nat_socket_list:
                    handle_nat_server_request(sock)
                elif sock in conn_proxied_socket_list:
                    print('v1版本 conn_proxied_socket_list size = 0')
                    # handle_proxied_response(sock)
                else:
                    continue

            # 执行任务
            if len(TASK_PROXY_HTTP_REQUEST_TO_PROXIED_SERVER_LIST) > 0 or len(TASK_PROXY_HTTP_RESPONSE_TO_NAT_SERVER_LIST) > 0:
                __process_task(nat_socket, proxied_host, proxied_port, TASK_PROXY_HTTP_REQUEST_TO_PROXIED_SERVER_LIST, TASK_PROXY_HTTP_RESPONSE_TO_NAT_SERVER_LIST)


        except socket.error as err:
            print("error: {}".format(err))
            break
        finally:
            pass


if __name__ == "__main__":
    main_loop()
