from client.close_conn_socket import close_nat_socket
from codec.nat_codec import nat_decode
from common.const import *
from nat_client_variable import *


# 处理 NAT Server 发送来的数据
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
    data = nat_decode(conn_nat_socket, cumulation, conn_nat_socket_fd_map)
    if data is NOT_WHOLE_FRAME:
        return

    command = data['command']
    if command == NAT_COMMAND_REQUEST:
        # 3.添加任务
        conn_nat_socket_task_list.append({
            "command": TASK_OPERATION_TO_PROXIED,
            "conn_proxy_socket_fd": data['conn_proxy_socket_fd'],
            "frame": data['frame']
        })