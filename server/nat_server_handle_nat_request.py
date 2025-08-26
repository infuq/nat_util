import json

from server.close_conn_socket import close_nat_socket
from codec.nat_codec import nat_decode
from common.const import *
from server.create_listen_socket import createProxyServerSocket
from server.nat_server_variable import *


# 处理 NAT Client 发送来的数据
def handle_nat_request(conn_nat_socket):
    cumulation = conn_nat_socket_fd_map[conn_nat_socket.fileno()][CUMULATOR_KEY]

    # 1.累加已接收数据
    while True:
        received_chunk = conn_nat_socket.recv(RECV_MAX_SIZE)
        if len(received_chunk) == 0 and len(cumulation) == 0:
            print(f'fd={conn_nat_socket.fileno()}断开连接')
            close_nat_socket(conn_nat_socket)
            return
        if len(received_chunk) == 0:
            break
        if len(received_chunk) < RECV_MAX_SIZE:
            cumulation = cumulation + received_chunk
            break
        cumulation = cumulation + received_chunk


    # 2.解码已接收数据
    frame = nat_decode(conn_nat_socket, cumulation, conn_nat_socket_fd_map)
    if frame is NOT_WHOLE_FRAME:
        return

    try:
        command = frame['command']
        if command == NAT_COMMAND_PROXY: # NAT Client 让 NAT Server 监听 proxy_port 端口

            proxy_protocol = frame['proxy_protocol']
            proxy_port = frame['proxy_port']
            proxy_port = int(proxy_port)
            proxy_server_socket = createProxyServerSocket(ip="0.0.0.0", port=proxy_port)

            listen_proxy_port_map[proxy_port] = {
                "proxy_protocol": proxy_protocol,
                "proxy_port": proxy_port,
                "proxy_server_socket": proxy_server_socket,
                "conn_nat_socket": conn_nat_socket,
            }
            listen_proxy_server_socket_list.append(proxy_server_socket)
        elif command == NAT_COMMAND_RESPONSE: # NAT Client 让 NAT Server 把数据返回给 Client
            conn_proxy_socket_fd = frame['conn_proxy_socket_fd']
            conn_proxy_socket = conn_proxy_socket_fd_map[conn_proxy_socket_fd][SOCKET_KEY]

            # 解码4个字节
            business_data_len = cumulation[LENGTH_COMMAND_LENGTH:LENGTH_FIELD_LENGTH + LENGTH_COMMAND_LENGTH]
            business_data_len = int.from_bytes(business_data_len, BYTE_ORDER)

            frame_len = LENGTH_COMMAND_LENGTH + LENGTH_FIELD_LENGTH + business_data_len
            # 解码业务数据
            frame = cumulation[LENGTH_COMMAND_LENGTH + LENGTH_FIELD_LENGTH:frame_len]

            frame = frame.decode()
            frame = json.loads(frame)

            data = frame['data']

            print(f'conn_proxy_socket_fd={conn_proxy_socket.fileno()}向Client发送数据')
            conn_proxy_socket.sendall(data.encode())

        else:
            print(f"Not supported request, client socket close, {conn_nat_socket}")
            close_nat_socket(conn_nat_socket)

    except Exception as err:
        print(err)
