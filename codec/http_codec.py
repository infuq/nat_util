import time

from common.const import *


"""
1.外网的 Client 与 NAT Server 通信
2.内网的 NAT Client 与 内网服务 通信
"""

# HTTP请求解码器
def http_decode_request(conn_socket, cumulation, socket_fd_map):

    # 查找请求头结束的位置 \r\n\r\n
    headers_end_index = cumulation.find(HTTP_HEADERS_END)
    if headers_end_index == -1:
        return NOT_WHOLE_FRAME

    # 请求头
    header = cumulation[0:headers_end_index]
    request_lines = header.decode().split("\r\n")
    method, path, protocol = request_lines[0].split(" ")
    request_headers = {
        'method': method,
        'path': path,
        'protocol': protocol
    }
    for line in request_lines[1:]:
        index = line.find(':')
        key = line[0:index]
        value = line[index+2:] # 跳过 `: ` 获取值

        if 'host' == key.lower():
            host, port = value.split(':')
            request_headers['host'] = host
            request_headers['port'] = port
        request_headers[key] = value


    content_length = 0
    frame_len = headers_end_index + len(HTTP_HEADERS_END) + content_length
    if 'Content-Length' in request_headers.keys():
        content_length = request_headers['Content-Length']
        content_length = int(content_length)
        frame_len = headers_end_index + len(HTTP_HEADERS_END) + content_length
        if len(cumulation) < frame_len:
            return NOT_WHOLE_FRAME
    else:
        print('请求头里没有Content-Length属性')

    # 跳过一个帧的长度
    socket_fd_map[conn_socket.fileno()][CUMULATOR_KEY] = cumulation[frame_len:]

    return {
        "request_headers": request_headers,
        "frame": cumulation[0:frame_len] # 完整的HTTP请求包
    }



# HTTP响应解码器
def http_decode_response(conn_socket, cumulation, socket_fd_map):

    # 查找响应头结束的位置
    headers_end_index = cumulation.find(HTTP_HEADERS_END)

    # 请求头
    header = cumulation[0:headers_end_index]
    request_lines = header.decode().split("\r\n")
    response_headers = { }
    for line in request_lines[1:]:
        index = line.find(':')
        key = line[0:index]
        value = line[index + 2:]  # 跳过 `: ` 获取值
        response_headers[key] = value

    content_length = 0
    frame_len = headers_end_index + len(HTTP_HEADERS_END) + content_length
    if 'Content-Length' in response_headers.keys():
        content_length = response_headers['Content-Length']
        content_length = int(content_length)
        frame_len = headers_end_index + len(HTTP_HEADERS_END) + content_length
        if len(cumulation) < frame_len:
            return NOT_WHOLE_FRAME
    else:
        print('响应头里没有Content-Length属性')

    # 跳过一个帧的长度
    socket_fd_map[conn_socket.fileno()][CUMULATOR_KEY] = cumulation[frame_len:]

    return {
        "response_headers": response_headers,
        "frame": cumulation[0:frame_len]  # 完整的HTTP响应包
    }
