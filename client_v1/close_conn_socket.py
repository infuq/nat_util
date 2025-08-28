from nat_client_variable import *


def close_nat_socket(conn_socket):
    try:
        conn_socket.close()
        if len(conn_nat_socket_list) > 0:
            conn_nat_socket_list.remove(conn_socket)
        if conn_socket in conn_nat_socket_fd_map.keys():
            del conn_nat_socket_fd_map[conn_socket]
    except Exception as e:
        print('close_nat_socket exception', e)


def close_proxy_socket(conn_proxy_socket):
    try:
        conn_proxy_socket.close()
        if len(conn_proxied_socket_list) > 0:
            conn_proxied_socket_list.remove(conn_proxy_socket)
        if conn_proxy_socket in conn_proxied_socket_fd_map.keys():
            del conn_proxied_socket_fd_map[conn_proxy_socket]
    except Exception as e:
        print('close_proxy_socket exception', e)