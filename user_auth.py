#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
#     FileName: user_auth.py
#         Desc: 2015-15/1/16:下午3:43
#       Author: 苦咖啡
#        Email: voilet@qq.com
#     HomePage: http://blog.kukafei520.net
#      History: 
# =============================================================================

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import time
import tornado.websocket
from tornado.escape import json_encode
from salt_api.salt_https_api import token_id, salt_api_token, salt_api_useradd
import nmap


from functools import partial, wraps
from concurrent.futures import ThreadPoolExecutor
import json
from websocket import create_connection
import tornado.gen
import tornado.concurrent
from tornado.concurrent import run_on_executor
# from salt.output import display_output
import yaml
from tornado.options import define, options
define('salt_api_url')
define('salt_api_pass')
define('salt_api_user')

EXECUTOR = ThreadPoolExecutor(max_workers=4)


def unblock(f):

    @tornado.web.asynchronous
    @wraps(f)
    def wrapper(*args, **kwargs):
        self = args[0]
        def callback(future):
            self.write(future.result())
            self.finish()

        EXECUTOR.submit(
            partial(f, *args, **kwargs)
        ).add_done_callback(
            lambda future: tornado.ioloop.IOLoop.instance().add_callback(
                partial(callback, future)))

    return wrapper


# class push_data(tornado.web.RequestHandler):
class user_add(tornado.web.RequestHandler):

    """注册方法"""

    # @tornado.web.asynchronous
    def get(self):
        self.write(json.dumps({"status": 403, "result": "error"}, indent=4))

    executor = ThreadPoolExecutor(2)
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        user = self.get_argument("user")
        gid = self.get_argument("gid")
        uid = self.get_argument("uid")
        key = self.get_argument("key")
        group = self.get_argument("group")
        self.write(json.dumps({"status": 200, "result": "OK"}, indent=4))
        self.finish()
        self.useradd(user, gid, uid, key, group)

    @run_on_executor
    def useradd(self, user, gid, uid, key, group):
        token_api_id = token_id()
        gid = "gid=%s" % (gid)
        uid = "uid=%s" % (uid)
        home = "home=/home/users/%s" %(user)
        shell = "shell=/bin/bash"
        print "111"
        # s = requests.post(salt_api_url, headers=headers, data='"client"="local", "fun"="user.add", "tgt"="hadoop01", [("arg",user), ("arg", gid), ("arg", uid), ("arg", home), ("arg", shell)]')
        list = salt_api_useradd(
            {'client': 'local', 'fun': 'user.add', 'tgt': "hadoop01",
            "arg": [user, gid, uid, home, shell], 'timeout': 100}, options.salt_api_url,
             {"X-Auth-Token": token_api_id}
        )
        master_status = list.run()
        print master_status
        # key = "%s" % (key)
        # add_key = salt_api_useradd(
        #     {'client': 'local', 'fun': 'cmd.script', 'tgt': "hadoop01",
        #     "arg": ["salt://usr/user_key.sh", user, key, group], 'timeout': 100}, salt_api_url,
        #      {"X-Auth-Token": token_api_id}
        # )
        # print add_key
        # master_status = add_key.run()
        # print "#" * 100
        # print master_status
        return True

# class push_data(tornado.web.RequestHandler):
class user_del(tornado.web.RequestHandler):

    """注册方法"""

    # @tornado.web.asynchronous
    def get(self):
        self.write(json.dumps({"status": 403, "result": "error"}, indent=4))

    executor = ThreadPoolExecutor(2)
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        user = self.get_argument("user")
        fqdn = self.get_argument("fqdn")
        self.write(json.dumps({"status": 200, "result": "OK"}, indent=4))
        self.finish()
        self.userdel(user, fqdn)

    @run_on_executor
    def userdel(self, user, fqdn):
        token_api_id = token_id()
        user = "gid=%s" % (user)

        # s = requests.post(salt_api_url, headers=headers, data='"client"="local", "fun"="user.add", "tgt"="hadoop01", [("arg",user), ("arg", gid), ("arg", uid), ("arg", home), ("arg", shell)]')
        list = salt_api_useradd(
            {'client': 'local', 'fun': 'user.delete', 'tgt': fqdn,
            "arg": [user, 'remove=True', 'force=True'], 'timeout': 100}, options.salt_api_url,
             {"X-Auth-Token": token_api_id}
        )
        master_status = list.run()
        print master_status

        return True