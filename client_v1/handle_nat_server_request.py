import json

from client_v1.close_conn_socket import close_nat_socket
from client_v1.handle_task import PROXY_HTTP_REQUEST_TO_PROXIED_SERVER_TASK_LIST
from codec.nat_codec import nat_decode
from common.const import *
from nat_client_variable import *


# 处理 NAT Server 发送来的数据
def handle_nat_server_request(conn_nat_socket):
    fd = conn_nat_socket.fileno()
    cumulation = conn_nat_socket_fd_dict[str(fd)][NAT_PARSER_REQUEST]

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

    conn_nat_socket_fd_dict[str(fd)][NAT_PARSER_REQUEST] = cumulation

    # 2.解码已接收数据
    data, frame_len = nat_decode(cumulation)
    if data == NOT_FULL_FRAME:
        return

    # 跳过一个帧的长度,存储剩下的字节
    conn_nat_socket_fd_dict[str(fd)][NAT_PARSER_REQUEST] = cumulation[frame_len:]

    try:
        command = data['command']
        frame = data['frame']
        if command == NAT_COMMAND_REQUEST:
            # 3.添加任务
            task = {
                "command": PROXY_HTTP_REQUEST_TO_PROXIED_SERVER_TASK,
                "data": frame
            }
            print(f'向PROXY_HTTP_REQUEST_TO_PROXIED_SERVER_TASK_LIST添加任务: {json.dumps(task)}')
            PROXY_HTTP_REQUEST_TO_PROXIED_SERVER_TASK_LIST.append(task)
    except Exception as err:
        print('handle_nat_server_request 异常', err)