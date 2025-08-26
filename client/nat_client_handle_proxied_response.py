from close_conn_socket import *
from common.const import *
from codec.http_codec import http_decode_response

def handle_proxied_response(conn_proxied_socket):

    cumulation = conn_proxied_socket_fd_map[conn_proxied_socket.fileno()][CUMULATOR_KEY]
    # 1.累加已接收数据
    while True:
        received_chunk = conn_proxied_socket.recv(RECV_MAX_SIZE)
        if len(received_chunk) == 0 and len(cumulation) == 0:
            print(f'fd={conn_proxied_socket.fileno()}断开连接')
            close_proxy_socket(conn_proxied_socket)
            return
        if len(received_chunk) == 0:
            break
        if len(received_chunk) < RECV_MAX_SIZE:
            cumulation = cumulation + received_chunk
            break
        cumulation = cumulation + received_chunk

    # 2.解码已接收数据
    data = http_decode_response(conn_proxied_socket, cumulation, conn_proxied_socket_fd_map)
    if data is NOT_WHOLE_FRAME:
        return


    # 3.添加任务
    conn_proxied_socket_task_list.append({
        "command": TASK_OPERATION_TO_NAT_SERVER,
        "conn_proxy_socket_fd": data['conn_proxy_socket_fd'],
        "frame": data['frame']
    })


def handle_proxied_response_direct(conn_proxied_socket):

    cumulation = conn_proxied_socket_fd_map[conn_proxied_socket.fileno()][CUMULATOR_KEY]
    # 1.累加已接收数据
    while True:
        received_chunk = conn_proxied_socket.recv(RECV_MAX_SIZE)
        if len(received_chunk) == 0 and len(cumulation) == 0:
            print(f'fd={conn_proxied_socket.fileno()}断开连接')
            close_proxy_socket(conn_proxied_socket)
            return
        if len(received_chunk) == 0:
            break
        if len(received_chunk) < RECV_MAX_SIZE:
            cumulation = cumulation + received_chunk
            break
        cumulation = cumulation + received_chunk

    # 2.解码已接收数据
    data = http_decode_response(conn_proxied_socket, cumulation, conn_proxied_socket_fd_map)
    if data is NOT_WHOLE_FRAME:
        return


    # 3.
    return {
        "command": TASK_OPERATION_TO_NAT_SERVER,
        "conn_proxy_socket_fd": data['conn_proxy_socket_fd'],
        "frame": data['frame']
    }
