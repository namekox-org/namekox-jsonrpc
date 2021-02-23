#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


from namekox_jsonrpc.core.proxy import JSONRpcProxy


class JSONRpc(object):
    def __init__(self, config):
        self.config = config
        self.proxy = JSONRpcProxy(config)

    @classmethod
    def name(cls):
        return 'jsonrpc'
