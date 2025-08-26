import argparse
import os
import re

import select

from client.connect_server_socket import *
from close_conn_socket import *
from codec.nat_codec import nat_encode
from common.const import *
from nat_client_handle_nat_request import handle_nat_request
from nat_client_handle_proxied_response import handle_proxied_response


def __init():
    parser = argparse.ArgumentParser(description="NAT Client")
    parser.add_argument("--proxy_protocol", help="Protocol of connection", required=True)
    parser.add_argument(
        "--proxy_port", type=int, help="Proxy port number", required=True
    )
    parser.add_argument(
        "--proxied_host", type=str, help="Proxied host", required=True
    )
    parser.add_argument(
        "--proxied_port", type=int, help="Proxied port number", required=True
    )

    args = parser.parse_args()

    nat_server = os.environ.get("NAT_SERVER")
    nat_server = "192.168.10.20:8090"
    nat_server_host, nat_server_port = nat_server.split(":")
    nat_server_port = int(nat_server_port)

    nat_socket = connect_nat_server(
        host=nat_server_host,
        port=nat_server_port,
    )

    data = {
        "proxy_protocol": args.proxy_protocol,
        "proxy_port": args.proxy_port
    }
    frame = nat_encode(data, NAT_COMMAND_PROXY)
    nat_socket.sendall(frame)

    conn_nat_socket_list.append(nat_socket)
    conn_nat_socket_fd_map[nat_socket.fileno()] = {
        CUMULATOR_KEY: EMPTY_MERGE_CUMULATOR,
        SOCKET_KEY: nat_socket
    }

    proxied_socket = connect_proxied_socket(
        host=args.proxied_host,
        port=args.proxied_port
    )
    conn_proxied_socket_list.append(proxied_socket)
    conn_proxied_socket_fd_map[proxied_socket.fileno()] = {
        CUMULATOR_KEY: EMPTY_MERGE_CUMULATOR,
        SOCKET_KEY: proxied_socket
    }

    return nat_socket, proxied_socket, args.proxied_host, args.proxied_port


def __process_task(nat_socket, proxied_socket, proxied_host, proxied_port, conn_nat_socket_task_list, conn_proxied_socket_task_list):

    for task in conn_nat_socket_task_list:
        command = task['command']
        if command == TASK_OPERATION_TO_PROXIED:
            print('将客户端发送来的请求转发给内网服务')

            conn_proxy_socket_fd = task['conn_proxy_socket_fd']
            frame = task['frame']
            frame = re.sub(r'(?<=Host: ).*(?=\r\n)', f'{proxied_host}:{proxied_port}', frame)

            method = frame.split('\r\n')[0].split(' ')[0]
            proxied_socket.sendall(frame.encode())


    conn_nat_socket_task_list.clear()

    for task in conn_proxied_socket_task_list:
        command = task['command']
        if command == TASK_OPERATION_TO_NAT_SERVER:
            print('将内网服务返回的响应转发给NAT SERVER')
            frame = task['frame']
            data = nat_encode(frame, NAT_COMMAND_RESPONSE)
            nat_socket.sendall(data)

    conn_proxied_socket_task_list.clear()



def main_loop():
    nat_socket, proxied_socket, proxied_host, proxied_port = __init()

    while True:
        try:

            read_socket_list = [
                sock
                for sock in (conn_nat_socket_list + conn_proxied_socket_list)
                if sock.fileno() != -1
            ]

            readable, writable, errored = select.select(read_socket_list, [], [], 0.5)

            for sock in readable:
                if sock in conn_nat_socket_list:
                    handle_nat_request(sock)
                elif sock in conn_proxied_socket_list:
                    handle_proxied_response(sock)
                else:
                    continue

            if len(conn_nat_socket_task_list) > 0 or len(conn_proxied_socket_task_list) > 0:
                __process_task(nat_socket, proxied_socket, proxied_host, proxied_port, conn_nat_socket_task_list, conn_proxied_socket_task_list)


        except socket.error as err:
            print("error: {}".format(err))
            break
        finally:
            pass


if __name__ == "__main__":
    main_loop()
