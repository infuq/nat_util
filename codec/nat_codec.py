import json

from common.const import *

"""
NAT Server 与 NAT Client 通信时使用自定义NAT通信协议, 需要用到编码器和解码器
"""

# 自定义NAT协议解码器
def nat_decode(cumulation):

    data_len = len(cumulation)
    if data_len < LENGTH_FIELD_LENGTH + LENGTH_COMMAND_LENGTH:
        return NOT_FULL_FRAME, None

    # 解码4个字节
    command = cumulation[0:LENGTH_COMMAND_LENGTH]
    command = int.from_bytes(command, BYTE_ORDER)

    # 解码4个字节
    business_data_len = cumulation[LENGTH_COMMAND_LENGTH:LENGTH_FIELD_LENGTH+LENGTH_COMMAND_LENGTH]
    business_data_len = int.from_bytes(business_data_len, BYTE_ORDER)

    frame_len = LENGTH_COMMAND_LENGTH + LENGTH_FIELD_LENGTH + business_data_len
    if data_len < frame_len:
        return NOT_FULL_FRAME, None

    # 解码业务数据
    frame = cumulation[LENGTH_COMMAND_LENGTH+LENGTH_FIELD_LENGTH:frame_len]

    frame = frame.decode()
    frame_obj = json.loads(frame)
    return {
        "command": command,
        "frame": frame_obj
    }, frame_len



# 自定义NAT协议编码器
def nat_encode(data, command):
    data = json.dumps(data)
    body = bytes(data, CHAR_SET)
    body_len = len(body)

    # 用4个字节存业务数据的类型
    command = command.to_bytes(LENGTH_COMMAND_LENGTH, BYTE_ORDER)

    # 用4个字节存body的长度
    length_field_len = body_len.to_bytes(LENGTH_FIELD_LENGTH, BYTE_ORDER)

    # 字节序列
    return command + length_field_len + body


