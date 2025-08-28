
from codec.http_codec import http_decode_request
from common.const import *
from server.close_conn_socket import close_proxy_socket
from server.nat_server_variable import *


# 处理 Client 发送来的HTTP请求数据
def handle_client_request(conn_proxy_socket):
    parser = conn_proxy_socket_fd_map[conn_proxy_socket.fileno()][HTTP_PARSER_REQUEST]

    # 2.解码
    data = http_decode_request(conn_proxy_socket, parser)

    if data == NEED_CLOSE_CONN:
        close_proxy_socket(conn_proxy_socket)
        return

    if data is NOT_FULL_FRAME:
        print('不是一个完整的帧1')
        return

    print('HTTP请求解码后数据', data)

    data['conn_proxy_socket_fd'] = conn_proxy_socket.fileno()
    # 3.添加任务
    task = {
        "command": TASK_PROXY_HTTP_REQUEST_TO_NAT_CLIENT,
        "data": data
    }
    print(f'向TASK_PROXY_HTTP_REQUEST_TO_NAT_CLIENT_LIST添加任务: {task}')
    TASK_PROXY_HTTP_REQUEST_TO_NAT_CLIENT_LIST.append(task)

