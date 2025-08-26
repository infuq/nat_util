import socket

def __create_connect_socket(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = (host, port)
    sock.connect(address)
    sock.setblocking(False)
    return sock

def connect_proxied_socket(host, port):
    return __create_connect_socket(host, port)

def connect_nat_server(host, port):
    return __create_connect_socket(host, port)