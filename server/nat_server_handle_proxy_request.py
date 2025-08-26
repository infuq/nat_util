from codec.http_codec import http_decode_request
from codec.nat_codec import nat_encode
from common.const import *
from server.close_conn_socket import close_proxy_socket
from server.nat_server_variable import *


# 处理 Client 发送来的请求数据
def handle_proxy_request(conn_proxy_socket):

    cumulation = conn_proxy_socket_fd_map[conn_proxy_socket.fileno()][CUMULATOR_KEY]
    # 1.累加已接收数据
    while True:
        received_chunk = conn_proxy_socket.recv(RECV_MAX_SIZE)
        if len(received_chunk) == 0 and len(cumulation) == 0:
            print(f'fd={conn_proxy_socket.fileno()}断开连接')
            close_proxy_socket(conn_proxy_socket)
            return
        if len(received_chunk) == 0:
            break
        if len(received_chunk) < RECV_MAX_SIZE:
            cumulation = cumulation + received_chunk
            break
        cumulation = cumulation + received_chunk


    # 2.解码已接收HTTP数据
    data = http_decode_request(conn_proxy_socket, cumulation, conn_proxy_socket_fd_map)
    if data is NOT_WHOLE_FRAME:
        return


    # 3.添加任务
    proxy_port = data['request_headers']['port']
    message = {
        "conn_proxy_socket_fd": conn_proxy_socket.fileno(),
        "frame": data['frame'].decode()
    }
    task = {
        "command": TASK_OPERATION_TO_NAT_CLIENT,
        "proxy_port": proxy_port,
        "message": message
    }
    conn_proxy_socket_task_list.append(task)
