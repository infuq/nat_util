RECV_MAX_SIZE               = 1024 * 1024  # 1MB


HTTP_HEADERS_END            = b'\x0d\x0a\x0d\x0a' # HTTP请求头的结束标志 \r\n\r\n
EMPTY_MERGE_CUMULATOR       = b''
NOT_WHOLE_FRAME             = None
LENGTH_FIELD_LENGTH         = 4
LENGTH_COMMAND_LENGTH       = 4


NAT_COMMAND_PROXY           = 1 # proxy
NAT_COMMAND_REQUEST         = 2 # request
NAT_COMMAND_RESPONSE        = 3 # response


BYTE_ORDER                  = 'big'
CHAR_SET                    = 'utf-8'
CUMULATOR_KEY               = 'cumulator' # 接收数据累加器
SOCKET_KEY                  = 'socket'



TASK_OPERATION_TO_NAT_CLIENT  = 1
TASK_OPERATION_TO_PROXIED     = 2
TASK_OPERATION_TO_NAT_SERVER  = 3