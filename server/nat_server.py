import argparse

import select

from common.const import *
from server.create_listen_socket import createNatServerSocket
from server.handle_client_request import handle_client_request
from server.handle_nat_client_request import handle_nat_client_request
from server.handle_task import process_proxy_http_request_to_nat_client_task
from server.nat_server_variable import *

try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser


def __init():
    parser = argparse.ArgumentParser(description="NAT Server")
    parser.add_argument("--port", help="Nat Server Port.", required=True)
    args = parser.parse_args()

    nat_server_socket = createNatServerSocket(ip="0.0.0.0", port=int(args.port))
    listen_nat_server_socket_list.append(nat_server_socket)


def main_loop():

    __init()

    try:
        while True:
            read_socket_list = [
                sock
                for sock in (listen_nat_server_socket_list + listen_proxy_server_socket_list + conn_nat_socket_list + conn_proxy_socket_list)
                if sock.fileno() != -1
            ]

            # 轮询IO事件
            readable, writable, errored = select.select(read_socket_list, [], [], 0.5)

            # 处理IO事件
            for sock in readable:
                if sock in listen_nat_server_socket_list: # NAT Client 连接 NAT Server
                    conn_socket, address = sock.accept()
                    conn_socket.setblocking(False)

                    conn_nat_socket_list.append(conn_socket)
                    conn_nat_socket_fd_map[conn_socket.fileno()] = {
                        NAT_PARSER_REQUEST: EMPTY_MERGE_CUMULATOR,
                        SOCKET_KEY: conn_socket
                    }
                    print(f"A New NAT Client Connection from: {address}, fd={conn_socket.fileno()}")
                elif sock in listen_proxy_server_socket_list: # Client <---> Proxy Server
                    conn_proxy_socket, address = sock.accept()
                    conn_proxy_socket.setblocking(False)

                    conn_proxy_socket_list.append(conn_proxy_socket)
                    conn_proxy_socket_fd_map[conn_proxy_socket.fileno()] = {
                        HTTP_PARSER_REQUEST: HttpParser(),
                        SOCKET_KEY: conn_proxy_socket
                    }
                    print(f"A New HTTP Client Connection from: {address}, fd={conn_proxy_socket.fileno()}")
                elif sock in conn_nat_socket_list:
                    handle_nat_client_request(sock)
                elif sock in conn_proxy_socket_list:
                    handle_client_request(sock)
                else:
                    continue

            # 执行任务
            if len(TASK_PROXY_HTTP_REQUEST_TO_NAT_CLIENT_LIST) > 0:
                process_proxy_http_request_to_nat_client_task(TASK_PROXY_HTTP_REQUEST_TO_NAT_CLIENT_LIST)

    except Exception as err:
        print(err)
    finally:
        for nat_server_socket in listen_nat_server_socket_list:
            nat_server_socket.close()
        for proxy_server_socket in listen_proxy_server_socket_list:
            proxy_server_socket.close()


if __name__ == "__main__":
    main_loop()
