# Install
```shell script
pip install -U namekox-jsonrpc
```

# Example
> ping.py
```python
# ! -*- coding: utf-8 -*-
#
# author: forcemain@163.com


from namekox_jsonrpc.constants import (
    DEFAULT_JSONRPC_CALL_MODE_ID,
    DEFAULT_JSONRPC_TB_CALL_MODE,
    DEFAULT_JSONRPC_YB_CALL_MODE
)
from namekox_jsonrpc.core.client import ServerProxy
from namekox_zookeeper.core.allotter import Allotter
from namekox_jsonrpc.core.entrypoints import jsonrpc
from namekox_webserver.core.entrypoints.app import app
from namekox_config.core.dependencies import ConfigHelper
from namekox_jsonrpc.constants import DEFAULT_JSONRPC_PORT
from namekox_context.core.dependencies import ContextHelper
from namekox_jsonrpc.core.messaging import gen_message_headers
from namekox_zookeeper.core.dependencies import ZooKeeperHelper
from namekox_zookeeper.constants import DEFAULT_ZOOKEEPER_SERVICE_ROOT_PATH


class Proxy(object):
    def __init__(self, service, protocol='http', timeout=None):
        self.service = service
        self.timeout = timeout
        self.protocol = protocol

    def __call__(self, protocol='http', timeout=None):
        self.timeout = timeout
        self.protocol = protocol

    def __getattr__(self, target_service):
        return Service(self, target_service)


class Service(object):
    def __init__(self, proxy, target_service):
        self.proxy = proxy
        self.target_service = target_service

    def __getattr__(self, target_method):
        return Method(self.proxy, self.target_service, target_method)


class Method(object):
    def __init__(self, proxy, target_service, target_method):
        self.target_method = target_method
        server = proxy.service.zk.allotter.get(target_service)
        uri = '{}://{}:{}'.format(proxy.protocol, server['address'], server['port'])
        timeout = proxy.timeout
        headers = gen_message_headers(proxy.service.ctx.data)
        self.target_service = ServerProxy(uri, headers=headers, timeout=timeout)

    def call_async(self, *args, **kwargs):
        kwargs.setdefault(DEFAULT_JSONRPC_CALL_MODE_ID, DEFAULT_JSONRPC_YB_CALL_MODE)
        return self.target_service.__getattr__(self.target_method)(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        kwargs.setdefault(DEFAULT_JSONRPC_CALL_MODE_ID, DEFAULT_JSONRPC_TB_CALL_MODE)
        return self.target_service.__getattr__(self.target_method)(*args, **kwargs)


SERVICE_NAME = 'ping'
SERVICE_PORT = DEFAULT_JSONRPC_PORT


class Ping(object):
    name = SERVICE_NAME
    description = u'PING服务'

    ctx = ContextHelper()
    cfg = ConfigHelper()
    zk = ZooKeeperHelper(
        name,
        allotter=Allotter(),
        roptions={'port': DEFAULT_JSONRPC_PORT},
        watching=DEFAULT_ZOOKEEPER_SERVICE_ROOT_PATH
    )

    @app.api('/api/ping/', methods=['GET'])
    def ping(self, request):
        target_service = Proxy(self).ping
        # call async
        target_service.pong.call_async()
        # call sync
        return target_service.pong()

    @jsonrpc.rpc(name='pong')
    def pong(self):
        print('Cur call stack: {}'.format(self.ctx.data))
        return 'pong'
```

# Running
> config.yaml
```yaml
JSONRPC:
  host: 0.0.0.0
  port: 5000
ZOOKEEPER:
  ping:
    hosts: 127.0.0.1:2181
WEBSERVER:
  host: 0.0.0.0
  port: 80
```
> namekox run ping
```shell script
2020-12-10 14:10:04,429 DEBUG load container class from namekox_core.core.service.container:ServiceContainer
2020-12-10 14:10:04,430 DEBUG starting services ['ping']
2020-12-10 14:10:04,430 DEBUG starting service ping entrypoints [ping:namekox_webserver.core.entrypoints.app.handler.ApiServerHandler:ping, ping:namekox_jsonrpc.core.entrypoints.rpc.server.XMLRpcServer:server, ping:namekox_jsonrpc.core.entrypoints.rpc.handler.XMLRpcHandler:pong, ping:namekox_webserver.core.entrypoints.app.server.WebServer:server]
2020-12-10 14:10:04,431 DEBUG spawn manage thread handle ping:namekox_jsonrpc.core.entrypoints.rpc.server:start_server(args=(), kwargs={}, tid=start_server)
2020-12-10 14:10:04,432 DEBUG spawn manage thread handle ping:namekox_webserver.core.entrypoints.app.server:handle_connect(args=(), kwargs={}, tid=handle_connect)
2020-12-10 14:10:04,433 DEBUG service ping entrypoints [ping:namekox_webserver.core.entrypoints.app.handler.ApiServerHandler:ping, ping:namekox_jsonrpc.core.entrypoints.rpc.server.XMLRpcServer:server, ping:namekox_jsonrpc.core.entrypoints.rpc.handler.XMLRpcHandler:pong, ping:namekox_webserver.core.entrypoints.app.server.WebServer:server] started
2020-12-10 14:10:04,433 DEBUG starting service ping dependencies [ping:namekox_zookeeper.core.dependencies.ZooKeeperHelper:zk, ping:namekox_context.core.dependencies.ContextHelper:ctx]
2020-12-10 14:10:04,434 INFO Connecting to 127.0.0.1:2181
2020-12-10 14:10:04,435 DEBUG Sending request(xid=None): Connect(protocol_version=0, last_zxid_seen=0, time_out=10000, session_id=0, passwd='\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', read_only=None)
2020-12-10 14:10:04,438 INFO Zookeeper connection established, state: CONNECTED
2020-12-10 14:10:04,438 DEBUG Sending request(xid=1): GetChildren(path='/namekox', watcher=<bound method ChildrenWatch._watcher of <kazoo.recipe.watchers.ChildrenWatch object at 0x10e9d9650>>)
2020-12-10 14:10:04,442 DEBUG Received response(xid=1): []
2020-12-10 14:10:04,471 DEBUG Sending request(xid=2): Exists(path='/namekox', watcher=None)
2020-12-10 14:10:04,474 DEBUG Received response(xid=2): ZnodeStat(czxid=74, mzxid=74, ctime=1606123632647, mtime=1606123632647, version=0, cversion=620, aversion=0, ephemeralOwner=0, dataLength=0, numChildren=0, pzxid=1210)
2020-12-10 14:10:04,475 DEBUG Sending request(xid=3): Create(path='/namekox/ping.2d70c7c7-e3e5-4602-9579-db6330a01017', data='{"port": 5000, "address": "127.0.0.1"}', acl=[ACL(perms=31, acl_list=['ALL'], id=Id(scheme='world', id='anyone'))], flags=1)
2020-12-10 14:10:04,481 DEBUG Received EVENT: Watch(type=4, state=3, path=u'/namekox')
2020-12-10 14:10:04,482 DEBUG Received response(xid=3): u'/namekox/ping.2d70c7c7-e3e5-4602-9579-db6330a01017'
2020-12-10 14:10:04,483 DEBUG Sending request(xid=4): GetChildren(path='/namekox', watcher=<bound method ChildrenWatch._watcher of <kazoo.recipe.watchers.ChildrenWatch object at 0x10e9d9650>>)
2020-12-10 14:10:04,484 DEBUG service ping dependencies [ping:namekox_zookeeper.core.dependencies.ZooKeeperHelper:zk, ping:namekox_context.core.dependencies.ContextHelper:ctx] started
2020-12-10 14:10:04,484 DEBUG services ['ping'] started
2020-12-10 14:10:04,485 DEBUG Received response(xid=4): [u'ping.2d70c7c7-e3e5-4602-9579-db6330a01017']
2020-12-10 14:10:04,485 DEBUG Sending request(xid=5): GetData(path='/namekox/ping.2d70c7c7-e3e5-4602-9579-db6330a01017', watcher=None)
2020-12-10 14:10:04,486 DEBUG Received response(xid=5): ('{"port": 5000, "address": "127.0.0.1"}', ZnodeStat(czxid=1212, mzxid=1212, ctime=1607580604476, mtime=1607580604476, version=0, cversion=0, aversion=0, ephemeralOwner=72091395573743677, dataLength=38, numChildren=0, pzxid=1212))
2020-12-10 14:10:06,440 DEBUG spawn manage thread handle ping:namekox_webserver.core.entrypoints.app.server:handle_request(args=(<eventlet.greenio.base.GreenSocket object at 0x10e9d9410>, ('127.0.0.1', 63862)), kwargs={}, tid=handle_request)
2020-12-10 14:10:06,443 DEBUG spawn worker thread handle ping:ping(args=(<Request 'http://127.0.0.1/api/ping/' [GET]>,), kwargs={}, context={})
2020-12-10 14:10:06,444 DEBUG spawn worker thread handle ping:pong(args=[], kwargs={}, context={'call_id_stack': ['374af089-7973-49f7-a5ae-79fd54a2617d']})
127.0.0.1 - - [10/Dec/2020 14:10:06] "POST /RPC2 HTTP/1.1" 200 -
Cur call stack: {'call_id_stack': ['374af089-7973-49f7-a5ae-79fd54a2617d', '8d18ee16-b579-4739-a901-52f90eb8684e']}
2020-12-10 14:10:06,446 DEBUG spawn worker thread handle ping:pong(args=[], kwargs={}, context={'call_id_stack': ['374af089-7973-49f7-a5ae-79fd54a2617d']})
Cur call stack: {'call_id_stack': ['374af089-7973-49f7-a5ae-79fd54a2617d', 'c527f9aa-9f22-46db-8b19-088b75c4a0c5']}
127.0.0.1 - - [10/Dec/2020 14:10:06] "POST /RPC2 HTTP/1.1" 200 -
127.0.0.1 - - [10/Dec/2020 14:10:06] "GET /api/ping/ HTTP/1.1" 200 239 0.006371
^C2020-12-10 14:10:08,278 DEBUG stopping services ['ping']
2020-12-10 14:10:08,278 DEBUG stopping service ping entrypoints [ping:namekox_webserver.core.entrypoints.app.handler.ApiServerHandler:ping, ping:namekox_jsonrpc.core.entrypoints.rpc.server.XMLRpcServer:server, ping:namekox_jsonrpc.core.entrypoints.rpc.handler.XMLRpcHandler:pong, ping:namekox_webserver.core.entrypoints.app.server.WebServer:server]
2020-12-10 14:10:08,279 DEBUG wait service ping entrypoints [ping:namekox_webserver.core.entrypoints.app.handler.ApiServerHandler:ping, ping:namekox_jsonrpc.core.entrypoints.rpc.server.XMLRpcServer:server, ping:namekox_jsonrpc.core.entrypoints.rpc.handler.XMLRpcHandler:pong, ping:namekox_webserver.core.entrypoints.app.server.WebServer:server] stop
2020-12-10 14:10:08,280 DEBUG service ping entrypoints [ping:namekox_webserver.core.entrypoints.app.handler.ApiServerHandler:ping, ping:namekox_jsonrpc.core.entrypoints.rpc.server.XMLRpcServer:server, ping:namekox_jsonrpc.core.entrypoints.rpc.handler.XMLRpcHandler:pong, ping:namekox_webserver.core.entrypoints.app.server.WebServer:server] stopped
2020-12-10 14:10:08,280 DEBUG stopping service ping dependencies [ping:namekox_zookeeper.core.dependencies.ZooKeeperHelper:zk, ping:namekox_context.core.dependencies.ContextHelper:ctx]
2020-12-10 14:10:08,280 DEBUG Sending request(xid=6): Close()
2020-12-10 14:10:08,284 DEBUG Received EVENT: Watch(type=4, state=3, path=u'/namekox')
2020-12-10 14:10:08,285 INFO Closing connection to 127.0.0.1:2181
2020-12-10 14:10:08,285 INFO Zookeeper session lost, state: CLOSED
2020-12-10 14:10:08,289 DEBUG service ping dependencies [ping:namekox_zookeeper.core.dependencies.ZooKeeperHelper:zk, ping:namekox_context.core.dependencies.ContextHelper:ctx] stopped
2020-12-10 14:10:08,290 DEBUG services ['ping'] stopped
2020-12-10 14:10:08,290 DEBUG killing services ['ping']
2020-12-10 14:10:08,290 DEBUG service ping already stopped
2020-12-10 14:10:08,290 DEBUG services ['ping'] killed
```
> curl http://127.0.0.1/api/ping/
```json
{
    "errs": "",
    "code": "Request:Success",
    "data": "pong",
    "call_id": "686acd52-2653-46a6-a7a0-64b53508762c"
}
```

# Integrate
```python
# ! -*- coding: utf-8 -*-
#
# author: forcemain@163.com


import time


from namekox_jsonrpc.core.client import ServerProxy
from namekox_jsonrpc.core.messaging import gen_message_headers

config = {
    'timeout': 5,
    'headers': gen_message_headers({}),
}

cur_time = time.time()
# http://${TARGET_SERVICE_HOST}:${TARGET_SERVICE_PORT}/
proxy = ServerProxy('http://127.0.0.1:5000/', **config)
value = proxy.pong()
print('Got cluster rpc result: {}, cost: {}s'.format(value, time.time()-cur_time))
```

# Debug
> config.yaml
```yaml
CONTEXT:
  - namekox_jsonrpc.cli.subctx.jsonrpc:XMLRpc
XMLRPC:
  host: 0.0.0.0
  port: 5000
ZOOKEEPER:
  ping:
    hosts: 127.0.0.1:2181
WEBSERVER:
  host: 0.0.0.0
  port: 80
```
> namekox shell
```shell script
Namekox Python 2.7.16 (default, Dec 13 2019, 18:00:32)
[GCC 4.2.1 Compatible Apple LLVM 11.0.0 (clang-1100.0.32.4) (-macos10.15-objc-s shell on darwin
In [1]: nx.jsonrpc.proxy('http://127.0.0.1:5000/').pong()
Out[1]: 'pong'
```
