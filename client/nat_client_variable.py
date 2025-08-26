conn_nat_socket_task_list = []
conn_proxied_socket_task_list = []

conn_nat_socket_list                = []
conn_proxied_socket_list            = []


"""
conn_nat_socket_fd_map[conn_socket.fileno()] = 
{
    "cumulator": EMPTY_MERGE_CUMULATOR,
    "socket": conn_socket
}
"""
conn_nat_socket_fd_map              = {}

"""
conn_proxied_socket_fd_map[conn_proxied_socket.fileno()] = 
{
    "cumulator": EMPTY_MERGE_CUMULATOR,
    "socket": conn_proxy_socket
}
"""
conn_proxied_socket_fd_map          = {}

