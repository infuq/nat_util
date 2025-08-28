import socket

def __create_connect_socket(host, port, blocking=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = (host, port)
    sock.connect(address)
    sock.setblocking(blocking)
    return sock

def connect_proxied_socket(host, port, blocking=False):
    return __create_connect_socket(host, port, blocking)

def connect_nat_server(host, port):
    return __create_connect_socket(host, port)