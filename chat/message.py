#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
#     FileName: message.py
#         Desc: 2015-15/2/26:下午9:42
#       Author: 苦咖啡
#        Email: voilet@qq.com
#     HomePage: http://blog.kukafei520.net
#      History: 
# =============================================================================

# coding: utf-8
import json
import tornado.websocket
from tornado.options import options
from chat.manager import ClientManager


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """
    允许所有websocket请求
    """

    def check_origin(self, origin):
        return True

    def open(self):
        """
        1, 检查当前客户端时候已经打开浏览器窗口，是，发送错误提示信息
        """
        print "websocket open"
        jid = self.get_argument('jid')
        ClientManager.add_client(str(id(self)), jid=jid, handler=self)

    def on_message(self, message):
        print message
        # pass

    def on_close(self):
        jid = self.get_argument('jid')
        _id = str(id(self))
        print "关闭id是:", _id
        ClientManager.remove_client(jid)

    def send_to_all(self, data):
        print "send all"
        ClientManager.publish(self.settings['redis'], options.redis_channel, data)
