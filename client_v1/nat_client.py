import argparse

import select

from client_v1.connect_server_socket import *
from client_v1.handle_nat_server_request import handle_nat_server_request
from client_v1.handle_task import run_all_tasks
from close_conn_socket import *
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
    conn_nat_socket_fd_dict[str(nat_socket.fileno())] = {
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
                    pass
                    # handle_proxied_response(sock)
                else:
                    continue

            # 执行任务
            run_all_tasks(nat_socket, proxied_host, proxied_port)

        except socket.error as err:
            print("error: {}".format(err))
            break
        finally:
            pass


if __name__ == "__main__":
    main_loop()
