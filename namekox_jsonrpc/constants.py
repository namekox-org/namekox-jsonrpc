#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


from namekox_core.core.generator import generator_port


JSONRPC_CONFIG_KEY = 'JSONRPC'
DEFAULT_JSONRPC_HOST = '0.0.0.0'
DEFAULT_JSONRPC_PORT = generator_port()
DEFAULT_JSONRPC_TB_CALL_MODE = 0
DEFAULT_JSONRPC_YB_CALL_MODE = 1
DEFAULT_JSONRPC_H_PREFIX = 'namekox-h'
DEFAULT_JSONRPC_CALL_MODE_ID = '__call_mode__'
