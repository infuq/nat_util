RECV_MAX_SIZE               = 1024 * 1024  # 1MB


HTTP_HEADERS_END            = b'\x0d\x0a\x0d\x0a' # HTTP请求头的结束标志 \r\n\r\n
EMPTY_MERGE_CUMULATOR       = b''
NOT_FULL_FRAME              = 'NOT_FULL_FRAME'
NEED_CLOSE_CONN             = 'NEED_CLOSE_CONN'
LENGTH_FIELD_LENGTH         = 4
LENGTH_COMMAND_LENGTH       = 4


NAT_COMMAND_PROXY           = 1 # proxy
NAT_COMMAND_REQUEST         = 2 # request
NAT_COMMAND_RESPONSE        = 3 # response


BYTE_ORDER                  = 'big'
CHAR_SET                    = 'utf-8'
SOCKET_KEY                  = 'socket'
NAT_PARSER_REQUEST          = 'nat_parser_request'
HTTP_PARSER_REQUEST         = 'http_parser_request'
HTTP_PARSER_RESPONSE        = 'http_parser_response'


PROXY_HTTP_REQUEST_TO_NAT_CLIENT_TASK       = 1
PROXY_HTTP_REQUEST_TO_PROXIED_SERVER_TASK   = 2
PROXY_HTTP_RESPONSE_TO_NAT_SERVER_TASK      = 3
