from close_conn_socket import *
from codec.http_codec import http_decode_response
from common.const import *


# 处理内网服务发送的HTTP响应
def handle_proxied_response(conn_proxied_socket):
    parser = conn_proxied_socket_fd_map[conn_proxied_socket.fileno()][HTTP_PARSER_RESPONSE]

    # 2.解码
    data = http_decode_response(conn_proxied_socket, parser)
    if data is NOT_FULL_FRAME:
        print('不是一个完整的帧2')
        return

    print('HTTP响应解码后数据', data)

    data['conn_proxy_socket_fd'] = conn_proxied_socket.fileno()
    # 3.添加任务
    task = {
        "command": TASK_PROXY_HTTP_RESPONSE_TO_NAT_SERVER,
        "data": data
    }
    print(f'向TASK_PROXY_HTTP_RESPONSE_TO_NAT_SERVER_LIST添加任务:{task}')
    TASK_PROXY_HTTP_RESPONSE_TO_NAT_SERVER_LIST.append(task)

