#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


from .rpc.handler import JSONRpcHandler


jsonrpc = type(__name__, (object,), {'rpc': JSONRpcHandler.decorator})
