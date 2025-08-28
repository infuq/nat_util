listen_nat_server_socket_list       = []
listen_proxy_server_socket_list     = []
conn_nat_socket_list                = []
conn_proxy_socket_list              = []

"""
listen_proxy_port_map[proxy_port] = {
    "proxy_protocol": proxy_protocol,
    "proxy_port": proxy_port,
    "proxy_server_socket": proxy_server_socket,
    "conn_nat_socket": conn_nat_socket
}
"""
listen_proxy_port_map               = {}

"""
conn_nat_socket_fd_map[conn_socket.fileno()] = {
    NAT_PARSER_REQUEST: EMPTY_MERGE_CUMULATOR,
    SOCKET_KEY: conn_socket
}
"""
conn_nat_socket_fd_map              = {}

"""
conn_proxy_socket_fd_map[conn_proxy_socket.fileno()] = {
    HTTP_PARSER_REQUEST: HttpParser(),
    HTTP_PARSER_RESPONSE: HttpParser(),
    SOCKET_KEY: conn_proxy_socket
}
"""
conn_proxy_socket_fd_map            = {}


TASK_PROXY_HTTP_REQUEST_TO_NAT_CLIENT_LIST = []