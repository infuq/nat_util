from nat_server_variable import *


def close_nat_socket(conn_socket):
    conn_nat_socket_list.remove(conn_socket)
    del conn_nat_socket_fd_map[conn_socket]
    conn_socket.close()

def close_proxy_socket(conn_proxy_socket):
    conn_proxy_socket_list.remove(conn_proxy_socket)
    del conn_proxy_socket_fd_map[conn_proxy_socket]
    conn_proxy_socket.close()
