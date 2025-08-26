import argparse

import select

from codec.nat_codec import nat_encode
from common.const import *
from server.create_listen_socket import createNatServerSocket
from server.nat_server_handle_nat_request import handle_nat_request
from server.nat_server_handle_proxy_request import handle_proxy_request
from server.nat_server_variable import *


def __init():
    parser = argparse.ArgumentParser(description="NAT Client")
    parser.add_argument("--port", help="Nat Server Port.", required=True)
    args = parser.parse_args()

    nat_server_socket = createNatServerSocket(ip="0.0.0.0", port=int(args.port))
    listen_nat_server_socket_list.append(nat_server_socket)


def __process_proxy_socket_task(conn_proxy_socket_task_list):
    for task in conn_proxy_socket_task_list:
        command = task['command']
        if command == TASK_OPERATION_TO_NAT_CLIENT:
            print('将客户端发送来的请求转发给NAT CLIENT')
            proxy_port = task['proxy_port']
            message = task['message']
            data = nat_encode(message, NAT_COMMAND_REQUEST)
            conn_nat_socket = listen_proxy_port_map[int(proxy_port)]["conn_nat_socket"]
            conn_nat_socket.sendall(data)

    conn_proxy_socket_task_list.clear()


def main_loop():

    __init()

    try:
        while True:
            read_socket_list = [
                sock
                for sock in (listen_nat_server_socket_list + listen_proxy_server_socket_list + conn_nat_socket_list + conn_proxy_socket_list)
                if sock.fileno() != -1
            ]

            readable, writable, errored = select.select(read_socket_list, [], [], 0.5)

            for sock in readable:
                if sock in listen_nat_server_socket_list: # NAT Server <---> NAT Client
                    conn_socket, address = sock.accept()
                    conn_socket.setblocking(False)

                    conn_nat_socket_list.append(conn_socket)
                    conn_nat_socket_fd_map[conn_socket.fileno()] = {
                        CUMULATOR_KEY: EMPTY_MERGE_CUMULATOR,
                        SOCKET_KEY: conn_socket
                    }
                    print(f"New NAT Client Connection from: {address}")
                elif sock in listen_proxy_server_socket_list: # Client <---> Proxy Server
                    conn_proxy_socket, address = sock.accept()
                    conn_proxy_socket.setblocking(False)

                    conn_proxy_socket_list.append(conn_proxy_socket)
                    conn_proxy_socket_fd_map[conn_proxy_socket.fileno()] = {
                        CUMULATOR_KEY: EMPTY_MERGE_CUMULATOR,
                        SOCKET_KEY: conn_proxy_socket
                    }
                    print(f"New Client Connection from: {address}, fd={conn_proxy_socket.fileno()}")
                elif sock in conn_nat_socket_list:
                    handle_nat_request(sock)
                elif sock in conn_proxy_socket_list:
                    handle_proxy_request(sock)
                else:
                    continue

            if len(conn_proxy_socket_task_list) > 0:
                __process_proxy_socket_task(conn_proxy_socket_task_list)

    except Exception as err:
        print(err)
    finally:
        for nat_server_socket in listen_nat_server_socket_list:
            nat_server_socket.close()
        for proxy_server_socket in listen_proxy_server_socket_list:
            proxy_server_socket.close()


if __name__ == "__main__":
    main_loop()
