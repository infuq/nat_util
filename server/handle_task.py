import json

from codec.nat_codec import nat_encode
from common.const import PROXY_HTTP_REQUEST_TO_NAT_CLIENT_TASK, NAT_COMMAND_REQUEST
from server.nat_server_variable import listen_proxy_port_dict

PROXY_HTTP_REQUEST_TO_NAT_CLIENT_TASK_LIST = []


def run_all_tasks():
    for task in PROXY_HTTP_REQUEST_TO_NAT_CLIENT_TASK_LIST:
        command = task['command']
        proxy_port = task['port']
        data = task['data']
        if command == PROXY_HTTP_REQUEST_TO_NAT_CLIENT_TASK:
            """ data = 
            {
                "method": "POST",
                "url": "/data/check/success",
                "headers": {
                    "Host": "192.168.10.13:38081",
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept": "*/*",
                    "Connection": "keep-alive",
                    "Content-Length": "48"
                },
                "body": {
                     "keyword": "红薯",
                     "k": "白糖"
                },
                "conn_proxy_socket_fd": 812
            }
            """
            print(f'将客户端的HTTP请求转发给NAT Client, data={json.dumps(data)}')
            encrypt_data = nat_encode(data, NAT_COMMAND_REQUEST)
            conn_nat_socket = listen_proxy_port_dict[str(proxy_port)]["conn_nat_socket"]
            conn_nat_socket.sendall(encrypt_data)

    PROXY_HTTP_REQUEST_TO_NAT_CLIENT_TASK_LIST.clear()
