from client_v1.handle_task import PROXY_HTTP_RESPONSE_TO_NAT_SERVER_TASK_LIST
from close_conn_socket import *
from codec.http_codec import http_decode_response
from common.const import *


# 处理内网服务发送的HTTP响应
def handle_proxied_response(conn_proxied_socket):
    fd = conn_proxied_socket.fileno()
    parser = conn_proxied_socket_fd_dict[str(fd)][HTTP_PARSER_RESPONSE]

    # 2.解码
    data = http_decode_response(conn_proxied_socket, parser)
    if data == NOT_FULL_FRAME:
        print('不是一个完整的帧')
        return

    data['conn_proxy_socket_fd'] = fd
    # 3.添加任务
    task = {
        "command": PROXY_HTTP_RESPONSE_TO_NAT_SERVER_TASK,
        "data": data
    }
    print(f'向TASK_PROXY_HTTP_RESPONSE_TO_NAT_SERVER_LIST添加任务:{task}')
    PROXY_HTTP_RESPONSE_TO_NAT_SERVER_TASK_LIST.append(task)

