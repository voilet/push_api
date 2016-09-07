#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
#     FileName: test.py
#         Desc: 2015-15/1/5:下午11:56
#       Author: 苦咖啡
#        Email: voilet@qq.com
#     HomePage: http://blog.kukafei520.net
#      History: 
# =============================================================================

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import logging
import uuid
import tornado.httpclient
# from settings import settings
# from push import push_data
# from functools import partial, wraps
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps
import time
import tornado.ioloop
import tornado.web
import commands
from user_auth import user_add
from tornado.options import define, options

define("port", default=8001, help="run on the given port", type=int)

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

# websocket
def send_message(message):
    for handler in ChatSocketHandler.socket_handlers:
        try:
            handler.write_message(message)
        except:
            logging.error('Error sending message', exc_info=True)

class ChatSocketHandler_test(tornado.websocket.WebSocketHandler):
    socket_handlers = set()

    def check_origin(self, origin):
        return True

    def open(self):
        print "socket opened"
        ChatSocketHandler.socket_handlers.add(self)
        send_message('A new user has entered the chat room.')

    def on_close(self):
        print "socketed closed"
        ChatSocketHandler.socket_handlers.remove(self)
        send_message('A user has left the chat room.')

    def on_message(self, message):
        print "*" * 100
        print message
        send_message(message)

class ChatSocketHandler(tornado.websocket.WebSocketHandler):

    connects = set()
    def check_origin(self, origin):
        return True

    def open(self):
        # print "socket opened"
        ChatSocketHandler.connects.add(self)

    def on_message(self, message):
        # name = self.get_argument("name")
        # self.write_message(name + message)
        ChatSocketHandler.send_all(message)
        # ChatSocketHandler.send_header(self.get_argument("name"), message)

    def on_close(self):
        pass
        print "socketed closed"

    @classmethod
    def send_all(cls, chat):
        for connect in cls.connects:
            try:
                connect.write_message(chat)
            except:
                pass


class BaseHandle(tornado.web.RequestHandler):
    # def initialize(self):
    #     self.session = DB_Session
    #
    # def on_finish(self):
    #     self.session.close()

    def get_current_user(self):
        return self.get_secure_cookie("user")

class MainHandler(tornado.web.RequestHandler):

    def get(self):

        self.write("Hello, world %s" % time.time())

class SleepHandler(tornado.web.RequestHandler):

    @unblock
    def get(self, n):
        time.sleep(float(n))
        return "Awake! %s" % time.time()

class create_ks(BaseHandle):
    """注册方法"""
    def get(self):
        status = {"status": 403, "messate": "提交参数不正确"}
        # self.render("register.html")
        return self.write(status)

    def post(self):
        """
        验证提交数据
        """
        server_templates = {
            "dell": "dell.cfg",
            "hp": "hp.cfg",
            "lenovl": "lenovo.cfg"
        }
        mac = self.get_argument("mac")
        ip = self.get_argument("ip")
        fqdn = self.get_argument("hostname")
        operating = self.get_argument("operating")
        usage = self.get_argument("usage")
        model = self.get_argument("model")
        if mac and fqdn and operating and usage and model:
            pxe_file = "pxe_ks/%s" % (server_templates.get(model))
            s = open(pxe_file, "r")
            f = s.readlines()
            config = open(mac, "w")
            for i in f:
                config.write(i)
            config.close()
            s.close()
            # ipmi_pxe = "ipmitool -I lanplus -H %s -U root -P %s chassis bootdev pxe" % (ip, "funshion")
            # ipmi_power = "ipmitool -I lanplus -H %s -U root -P %s chassis power reset" % (ip, "funshion")
            # status,ipmi_data = commands.getstatusoutput(ipmi_pxe)
            # if status:
            #     commands.getoutput(ipmi_power)
            #     result = "配置文件生成完毕，已切换pxe装机模式并重启"
            # else:
            #     result = "配置文件生成完毕，远控卡操作失败，请手动登录远控卡，选择下次启动pxe并重启服务器"
            return self.write({"status": 200, "result": "请手动登录远控卡，选择下次启动pxe并重启服务器\n"
                                                        "或通过ipmitool控制远控卡重启\n"
                                                        "'ipmitool -I lanplus -H ip -U root -P xxx chassis bootdev pxe '下次启动pxe模式"
                                                        "ipmitool -I lanplus -H ip -U root -P xxx chassis power reset重启服务器"})

        rst = "%s %s" % (ip, u"参数不正确！请确认主机名，mac,服务器型号和系统版本是否正确")

        return self.write({"status": 403, "result": rst})

class test(tornado.web.RequestHandler):
    """
    注册方法
    """
    def get(self):
        status = {"status": 403, "messate": "提交参数不正确"}
        # self.render("register.html")
        self.write("Hello, world %s" % time.time())

# if __name__ == "__main__":
#     tornado.options.parse_command_line()

    # app = tornado.web.Application(
    # handlers=[
    #     (r"/", MainHandler),
    #     (r"/clone/create-physical-instances", create_ks),
    #     (r"/swan_api/$", push_data),
    #     (r"/sleep/(\d+)", SleepHandler),
    #     (r"/user/delete/", SleepHandler),
    #     (r"/user/add/", user_add),
    #     (r"/websocket", ChatSocketHandler),
    #     ], **settings
    # )

    # http_server = tornado.httpserver.HTTPServer(app)
    # http_server.listen(options.port)
    # tornado.ioloop.IOLoop.instance().start()