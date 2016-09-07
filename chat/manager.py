#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
#     FileName: manager.py
#         Desc: 2015-15/2/26:下午9:43
#       Author: 苦咖啡
#        Email: voilet@qq.com
#     HomePage: http://blog.kukafei520.net
#      History: 
# =============================================================================

import json, time
from tornado.log import app_log
from chat.model import Client


class ClientManager(object):
    _CLIENTS_MAP = {}

    @classmethod
    def get_clients(cls):
        """
        获取当前连接的clients

        @return:
        """
        return cls._CLIENTS_MAP

    @classmethod
    def get_client_by_email(cls, jid):
        """
        根据websocket handler id获取当前连接client
        防止websocket还未创建成功,数据已经写入redis,在此方法中使用所有消息延迟1秒发送
        @param identity:
        @return:
        """
        # print "获取当前id", jid
        # time.sleep(1)
        app_log.info("current clients {0}".format(cls.get_clients()))
        try:
            client = cls._CLIENTS_MAP[jid]
            return client
        except Exception as ex:
            return None

    @classmethod
    def add_client(cls, identity, jid=None, handler=None):
        """
        添加新的client
        @param identity: websocket handler 编号
        @param nickname: 用户昵称
        @param email: 用户邮箱地址 唯一值
        @param handler : websocket handler实例对象
        @return:
        """
        # print "增加websocket会话id", identity, jid
        client = Client(identity, jid=jid, handler=handler)
        cls._CLIENTS_MAP[jid] = client
        return client

    @classmethod
    def remove_client(cls, jid):
        """
        移除client
        @param email:
        """
        app_log.debug("remove client[{0}]".format(jid))
        del cls._CLIENTS_MAP[jid]

    @classmethod
    def send_to_all(cls, data):

        """
        向所有链接到当前服务器的客户端发送信息
        @param data:
        """
        clients = cls.get_clients()
        for key in clients.keys():
            try:
                clients[key].handler.write_message(json.dumps(data))
            except Exception as ex:
                app_log.exception(ex)

    @classmethod
    def send_to(cls, to_email, data):

        """
        向特定用户发送消息
        @param source_email: 发送者邮箱
        @param to_email: 接受者邮箱地址
        @param data:
        """
        to_email = cls.get_client_by_email(to_email)

        try:
            # print data
            # print type(data)
            to_email.handler.write_message(json.dumps(data))
        except:
            # print "error"
            # print data
            pass

    @classmethod
    def publish(cls, redis=None, channel=None, message=None):
        redis.publish(channel, message)

    @classmethod
    def is_effective_connect(cls, handlerid):
        for key in cls._CLIENTS_MAP.keys():
            client = cls._CLIENTS_MAP[key]
            if client.identity == handlerid:
                return True
        return False

    @classmethod
    def is_client_connected(cls, jid):
        """
        检查当前连接的客户端是否已经打开了多个浏览器窗口
        @param email: 用户登录用的电子邮箱地址
        """
        try:
            client = cls.get_client_by_email(jid)
            if client:
                return True
        except Exception as ex:
            return False
