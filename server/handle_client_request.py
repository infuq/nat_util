
from codec.http_codec import http_decode_request
from common.const import *
from server.close_conn_socket import close_proxy_socket
from server.handle_task import PROXY_HTTP_REQUEST_TO_NAT_CLIENT_TASK_LIST
from server.nat_server_variable import *


# 处理 Client 发送来的HTTP请求数据
def handle_client_request(conn_proxy_socket):
    fd = conn_proxy_socket.fileno()
    parser = conn_proxy_socket_fd_dict[str(fd)][HTTP_PARSER_REQUEST]

    data, port = http_decode_request(conn_proxy_socket, parser)
    if data == NEED_CLOSE_CONN:
        close_proxy_socket(conn_proxy_socket)
        return
    if data == NOT_FULL_FRAME:
        print('不是一个完整的帧')
        return

    data['conn_proxy_socket_fd'] = fd
    task = {
        "command": PROXY_HTTP_REQUEST_TO_NAT_CLIENT_TASK,
        "port": port,
        "data": data
    }
    print(f'HTTP请求解码之后向PROXY_HTTP_REQUEST_TO_NAT_CLIENT_TASK_LIST添加任务: {task}')
    PROXY_HTTP_REQUEST_TO_NAT_CLIENT_TASK_LIST.append(task)

