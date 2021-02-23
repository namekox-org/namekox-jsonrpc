#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


from logging import getLogger
from namekox_webserver.core.entrypoints.app.server import WebServer
from namekox_jsonrpc.constants import JSONRPC_CONFIG_KEY, DEFAULT_JSONRPC_HOST, DEFAULT_JSONRPC_PORT


logger = getLogger(__name__)


class JSONRpcServer(WebServer):
    def setup(self):
        if self.host is not None and self.port is not None and self.sslargs is not None and self.srvargs is not None:
            return
        config = self.container.config.get(JSONRPC_CONFIG_KEY, {}).copy()
        self.middlewares = config.pop('middlewares', []) or []
        self.host = config.pop('host', DEFAULT_JSONRPC_HOST) or DEFAULT_JSONRPC_HOST
        self.port = config.pop('port', DEFAULT_JSONRPC_PORT) or DEFAULT_JSONRPC_PORT
        self.sslargs = {k: config.pop(k) for k in config if k in self.SSL_ARGS}
        self.sslargs and self.sslargs.update({'server_side': True})
        self.srvargs = config
