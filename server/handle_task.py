from common.const import TASK_PROXY_HTTP_REQUEST_TO_NAT_CLIENT, NAT_COMMAND_REQUEST
from codec.nat_codec import nat_encode
import json

from server.nat_server_variable import listen_proxy_port_map


def process_proxy_http_request_to_nat_client_task(TASK_PROXY_HTTP_REQUEST_TO_NAT_CLIENT_LIST):
    for task in TASK_PROXY_HTTP_REQUEST_TO_NAT_CLIENT_LIST:
        command = task['command']
        data = task['data']
        if command == TASK_PROXY_HTTP_REQUEST_TO_NAT_CLIENT:
            """
            {
                "port": 38081,
                "method": "POST",
                "url": "/query",
                "headers": {
                    "Host": "192.168.10.13:38081",
                    "port": 38081,
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
                "conn_proxy_socket_fd": 452
            }

            """
            print(f'将客户端的HTTP请求转发给NAT Client, data={json.dumps(data)}')
            proxy_port = data['port']
            encrypt_data = nat_encode(data, NAT_COMMAND_REQUEST)
            conn_nat_socket = listen_proxy_port_map[str(proxy_port)]["conn_nat_socket"]
            conn_nat_socket.sendall(encrypt_data)

    TASK_PROXY_HTTP_REQUEST_TO_NAT_CLIENT_LIST.clear()

