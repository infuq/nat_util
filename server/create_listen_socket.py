import socket

def __create_server_socket(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(5)
    return server_socket

def createNatServerSocket(ip, port):
    print(f"NatServer: '{ip}:{port}', running...")
    return __create_server_socket(ip, port)


def createProxyServerSocket(ip, port):
    print(f"ProxyServer: '{ip}:{port}', running...")
    return __create_server_socket(ip, port)