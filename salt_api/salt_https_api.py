#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
#     FileName:
#         Desc:
#       Author: 苦咖啡
#        Email: voilet@qq.com
#     HomePage: http://blog.kukafei520.net
#      Version: 0.0.1
#   LastChange: 
#      History:
# =============================================================================

import urllib2, cookielib, urllib, yaml, json
import requests
from conf.config import salt_api_url, salt_api_pass, salt_api_user
import redis

requests.packages.urllib3.disable_warnings()


class salt_api_token(object):
    def __init__(self, data, url, token=None):
        self.data = data
        self.url = url
        self.headers = {
            'User-agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            "Accept": "application/x-yaml",
        }
        self.headers.update(token)

    def run(self):
        print self.data
        req = requests.post(self.url, headers=self.headers, data=self.data, verify=False)
        context = req.text
        return yaml.load(context)


class salt_api_jobs(object):
    def __init__(self, url, token=None):
        self.url = url
        self.headers = {
            'User-agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            "Accept": "application/x-yaml",
        }
        self.headers.update(token)

    def run(self):
        context = urllib2.Request(self.url, headers=self.headers)
        resp = urllib2.urlopen(context)
        context = resp.read()
        return yaml.load(context)


def token_id():
    key_redis = redis.Redis("192.168.111.101", port=6379, db=0)
    salt_key = key_redis.get("salt_key")
    if not salt_key:
        s = salt_api_token(
            {
                "username": salt_api_user,
                "password": salt_api_pass,
                "eauth": "pam"
            },
            salt_api_url + "login",
            {}
        )
        test = s.run()
        salt_token = [i["token"] for i in test["return"]]
        salt_token = salt_token[0]
        key_redis.set("salt_key", salt_token)
        key_redis.expire("salt_key", 10800)
        return salt_token
    else:
        return salt_key


class salt_api_useradd(object):
    def __init__(self, data, url, token=None):
        self.data = data
        self.url = url
        self.headers = {
            'User-agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            "Accept": "application/x-yaml",
        }
        self.headers.update(token)

    def run(self):
        print self.data
        req = requests.post(self.url, headers=self.headers, data=self.data, verify=False)
        context = req.text
        return yaml.load(context)
