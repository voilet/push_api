#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
#     FileName: swan.py
#         Desc: 2014-14/12/30:下午1:36
#       Author: 苦咖啡
#        Email: voilet@qq.com
#     HomePage: http://blog.kukafei520.net
#      History: 
# =============================================================================

import requests
from tornado.options import define, options

from conf.config import salt_api_url, salt_api_user, salt_api_pass, config_url

class open_service(object):

    def __init__(self, serverName, ip=None):
        self.serverName = serverName
        self.ip = ip
        self.headers = {
            'User-agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            "Accept": "application/json",
        }


    def push(self):
        url = "%s/autoDeploy/push?serverName=%s" % (config_url, self.serverName)
        req = requests.get(url, headers=self.headers)
        context = req.json()
        return context

    def online_run(self):
        url = "%s/autoDeploy/online?serverName=%s&ip=%s" % (config_url, self.serverName, self.ip)
        print url
        try:
            req = requests.get(url, headers=self.headers)
            context = req.json()
            print context
        except:
            context = {"retCode": 503, "retMsg": req.text}
        return context

    def offline_run(self):
        url = "%s/autoDeploy/offline?serverName=%s&ip=%s" % (config_url, self.serverName, self.ip)
        try:
            req = requests.get(url, headers=self.headers)
            context = req.json()
            print context
        except:
            context = {"retCode": 503, "retMsg": req.text}
        return context

if __name__ == '__main__':
    status = {"retCode": 1}
    Open_push = open_service("OpenSubscribNotifyBackend")
    rest = Open_push.push()

    # if not rest:
    #     print "推送api请求失败"
    #     status["retCode"] = 0
    # else:
    #     print "推送api请求完成"
    #
    if status["retCode"]:
        up_server = open_service("OpenSubscribNotifyBackend", "192.168.135.242")
        rest = up_server.online_run()

        if rest:
            print "上线成功"
    else:
        print "上线失败"

    # if status["retCode"]:
    #     down_server = open_service("OpenSubscribNotifyBackend", "192.168.135.243")
    #     rest = down_server.online_run()
    #
    #     if rest:
    #         print "下线成功"
    # else:
    #     print "下线失败"


