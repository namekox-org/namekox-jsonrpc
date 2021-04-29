#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


import json
import urllib
import socket
import urllib2


from functools import partial
from logging import getLogger
from namekox_jsonrpc.exceptions import RpcTimeout
from namekox_core.exceptions import gen_data_to_exc
from namekox_jsonrpc.constants import DEFAULT_JSONRPC_CALL_MODE_ID, DEFAULT_JSONRPC_TB_CALL_MODE


logger = getLogger(__name__)


class ServerProxy(object):
    def __init__(self, uri, headers=None, timeout=None):
        protocol, uri = urllib.splittype(uri)
        errs = 'unsupported JSON-RPC protocol'
        protocol not in ('http', 'https') and self._raise(IOError, errs)
        self.protocol = protocol
        self._headers = headers or {}
        self._timeout = timeout or 3
        self._address = urllib.splithost(uri)[0]
        self._headers.setdefault('Content-Type', 'application/json')

    def _raise(self, exc, errs=None):
        raise (exc if errs is None else exc(errs))

    def _post(self, method, *args, **kwargs):
        url = '{}://{}/{}'.format(self.protocol, self._address, method)
        logger.debug('post {} with args={}, kwargs={}'.format(url, args, kwargs))
        kwargs.setdefault(DEFAULT_JSONRPC_CALL_MODE_ID, DEFAULT_JSONRPC_TB_CALL_MODE)
        req = urllib2.Request(
            url=url,
            headers=self._headers,
            data=json.dumps({'args': args, 'kwargs': kwargs}))
        try:
            rsp = urllib2.urlopen(req, timeout=self._timeout)
            res = json.loads(rsp.read())
        except socket.timeout:
            self._raise(RpcTimeout, self._timeout)
        err = res['errs']
        err and self._raise(gen_data_to_exc(err))
        return res['data']

    def __getattr__(self, name):
        return partial(self._post, name)
