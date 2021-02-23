#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import unicode_literals


import sys
import json


from eventlet import Event
from werkzeug import Response
from logging import getLogger
from werkzeug.routing import Rule
from namekox_jsonrpc.constants import (
    DEFAULT_JSONRPC_CALL_MODE_ID,
    DEFAULT_JSONRPC_TB_CALL_MODE,
    DEFAULT_JSONRPC_YB_CALL_MODE
)
from namekox_core.exceptions import gen_exc_to_data
from namekox_core.core.friendly import as_wraps_partial
from namekox_core.core.service.entrypoint import Entrypoint
from namekox_jsonrpc.core.messaging import get_message_headers


from .server import JSONRpcServer


logger = getLogger(__name__)


class BaseJSONRpcHandler(Entrypoint):
    server = JSONRpcServer()

    def __init__(self, name=None, **kwargs):
        self.name = name
        self.methods = ['POST']
        super(BaseJSONRpcHandler, self).__init__(**kwargs)

    @property
    def url_rule(self):
        rule = self.name or self.obj_name
        rule = '/{}'.format(rule)
        return Rule(rule, methods=['POST'], endpoint=self)

    def setup(self):
        self.server.register_extension(self)

    def stop(self):
        self.server.unregister_extension(self)
        self.server.wait_extension_stop()

    def handle_request(self, request):
        context, result, exc_info = None, None, None
        try:
            data = json.loads(request.data)
            ctxdata = get_message_headers(request)
            args, kwargs = data['args'], data['kwargs']
            mode = kwargs.pop(DEFAULT_JSONRPC_CALL_MODE_ID, DEFAULT_JSONRPC_TB_CALL_MODE)
            event = Event()
            res_handler = as_wraps_partial(self.res_handler, event)
            self.container.spawn_worker_thread(self, args, kwargs,
                                               ctx_data=ctxdata,
                                               res_handler=res_handler)
            if mode == DEFAULT_JSONRPC_TB_CALL_MODE:
                context, result, exc_info = event.wait()
            if mode == DEFAULT_JSONRPC_YB_CALL_MODE:
                context, result, exc_info = None, None, None
        except Exception:
            exc_info = sys.exc_info()
        return context, result, exc_info

    @staticmethod
    def res_handler(event, context, result, exc_info):
        data = (context, result, exc_info)
        event.send(data)
        return result, exc_info

    def handle_response(self, request, context, result):
        raise NotImplementedError

    def handle_exception(self, request, context, exc_info):
        raise NotImplementedError


class JSONRpcHandler(BaseJSONRpcHandler):
    def handle_request(self, request, *params):
        context, result, exc_info = super(JSONRpcHandler, self).handle_request(request)
        return (
            self.handle_response(request, context, result)
            if exc_info is None else
            self.handle_exception(request, context, exc_info)
        )

    def handle_response(self, request, context, result):
        payload = {'data': result, 'errs': None}
        payload = json.dumps(payload)
        headers = {'Content-Type': 'application/json'}
        return Response(payload, status=200, headers=headers)

    def handle_exception(self, request, context, exc_info):
        exc_type, exc_value, exc_trace = exc_info
        errs = gen_exc_to_data(exc_value)
        payload = {'data': None, 'errs': errs}
        payload = json.dumps(payload)
        headers = {'Content-Type': 'application/json'}
        return Response(payload, status=200, headers=headers)
