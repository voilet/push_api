#!/usr/bin/env python
#-*- coding: utf-8 -*-
#=============================================================================
#     FileName:
#         Desc:
#       Author: 苦咖啡
#        Email: voilet@qq.com
#     HomePage: http://blog.kukafei520.net
#      Version: 0.0.1
#   LastChange: 2013-02-20 14:52:11
#      History:
#=============================================================================


import os

#配置路由规则url
# settings = {
#     'debug': True,   #此为调试模式，正式环境必须关闭
#     'static_path': os.path.join(os.path.dirname(__file__), "static"),
#     'template_path': os.path.join(os.path.dirname(__file__), "templates"),
#     "cookie_secret": "8i$2jaau-_w%yqwazz7xikka*^ekkvmn$4+25v8&amp;ngz+$&amp;qy#3",
#     "login_url": "/login",
#     # "xsrf_cookies": True,
# }

import os
from os.path import abspath, dirname

import redis
import tornado.httpserver
import tornado.web
from tornado.log import app_log
from tornado.options import define, options
from urls import handlers
from chat import Listener

PROJECT_DIR = dirname(dirname(abspath(__file__)))
TEMPLATE_DIR = os.path.join(PROJECT_DIR, 'templates')
STATIC_DIR = os.path.join(PROJECT_DIR, 'static')
CONF_DIR = os.path.join(PROJECT_DIR, 'swan_api/conf')
CONF_FILE = CONF_DIR+os.path.sep+"application.conf"



define('redis_host', default='localhost')
define('redis_db', default=2, type=int)
define('redis_channel', default='web_chat', help='message pubsub channel')
define("debug", default=True, type=bool)
define("port", default=8888, type=int)


class Application(tornado.web.Application):

    _CLIENTS_MAP = {}

    def __init__(self):

        r = redis.Redis(host=options.redis_host, db=options.redis_db)
        client = Listener(r, [options.redis_channel])

        client.start()
        settings = {
            "template_path": TEMPLATE_DIR,
            "static_path": STATIC_DIR,
            "login_url": "/",
            "debug": options.debug,
            "redis": r,
            "cookie_secret": "8i$2jaau-_w%yqwazz7xikka*^ekkvmn$4+25v8&amp;ngz+$&amp;qy#3",
            "xsrf_cookies": False,
        }
        tornado.web.Application.__init__(self, handlers, **settings)


def run():
    """
    start chat application

    """
    tornado.options.parse_command_line()
    tornado.options.parse_config_file(CONF_FILE)
    port = os.environ.get("PORT", options.port)
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(port)
    # app_log.info("application run on {0}".format(port))
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass



if __name__ == "__main__":
    application = Application()

