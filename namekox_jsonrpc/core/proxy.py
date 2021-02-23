#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


from namekox_jsonrpc.core.client import ServerProxy


class JSONRpcProxy(object):
    def __init__(self, config, **options):
        self.config = config
        self.options = options

    def __call__(self, uri, **options):
        self.options.update(options)
        return ServerProxy(uri, **options)
