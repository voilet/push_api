#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
#     FileName: git_class.py
#         Desc: 2015-15/11/20:下午4:43
#       Author: 苦咖啡
#        Email: voilet@qq.com
#     HomePage: http://blog.kukafei520.net
#      History: 
# =============================================================================
import requests
from salt_api.salt_https_api import token_id, salt_api_token
from conf.config import salt_api_url, salt_api_pass, salt_api_user


class SaltApiGit(object):
    """pxe api接口"""

    def __init__(self, **kwargs):
        self.data = kwargs

        self.headers = {
            'CustomUser-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
            "Accept": "application/x-yaml",
        }
        s = {'expr_form': 'list'}
        self.data.update(s)

    def checkout(self):
        """执行"""
        code_checkout = salt_api_token(
            {'client': 'local',
             'fun': 'git.checkout',
             'tgt': self.data.get("tgt"),
             "arg": self.data.get("arg"),
             'timeout': 100,
             'expr_form': 'list'},
            salt_api_url,
            {"X-Auth-Token": self.data.get("token_api_id")}
        )
        rst = code_checkout.run()
        return rst

    def config_set(self):
        """执行"""
        code_checkout = salt_api_token(
            {'client': 'local',
             'fun': 'git.config_set',
             'tgt': self.data.get("tgt"),
             "arg": self.data.get("arg"),
             'timeout': 100,
             'expr_form': 'list'},
            salt_api_url,
            {"X-Auth-Token": self.data.get("token_api_id")}
        )
        rst = code_checkout.run()
        return rst

    def setemail(self):
        """执行"""
        code_checkout = salt_api_token(
            {'client': 'local',
             'fun': 'git.config_set',
             'tgt': self.data.get("tgt"),
             "arg": self.data.get("arg"),
             'timeout': 100,
             'expr_form': 'list'},
            salt_api_url,
            {"X-Auth-Token": self.data.get("token_api_id")}
        )
        rst = code_checkout.run()
        return rst

    def pull(self):
        code_pull = salt_api_token(
            {'client': 'local',
             'fun': 'git.pull',
             'tgt': self.data.get("tgt"),
             "arg": self.data.get("arg"),
             'timeout': 100,
             'expr_form': 'list'},
            salt_api_url,
            {"X-Auth-Token": self.data.get("token_api_id")}
        )
        rst = code_pull.run()
        return rst

    def push(self):
        code_push = salt_api_token(
            {'client': 'local',
             'fun': 'git.push',
             'tgt': self.data.get("tgt"),
             "arg": self.data.get("arg"),
             'timeout': 100,
             'expr_form': 'list'},
            salt_api_url,
            {"X-Auth-Token": self.data.get("token_api_id")}

        )
        rst = code_push.run()

        return rst

    def reset(self):
        code_pull = salt_api_token(
            {'client': 'local',
             'fun': 'git.reset',
             'tgt': self.data.get("tgt"),
             "arg": self.data.get("arg"),
             'timeout': 100,
             'expr_form': 'list'},
            salt_api_url,
            {"X-Auth-Token": self.data.get("token_api_id")}
        )
        rst = code_pull.run()
        return rst

    def version(self):
        code_pull = salt_api_token(
            {'client': 'local',
             'fun': 'git.revision',
             'tgt': self.data.get("tgt"),
             "arg": self.data.get("arg"),
             'timeout': 100,
             'expr_form': 'list'},
            salt_api_url,
            {"X-Auth-Token": self.data.get("token_api_id")}
        )
        rst = code_pull.run()
        return rst

    def CmdRun(self):
        code_pull = salt_api_token(
            {'client': 'local',
             'fun': 'cmd.run',
             'tgt': self.data.get("tgt"),
             "arg": [self.data.get("arg"), "env='{\"LC_ALL\": \"zh_CN.UTF-8\"}'"],
             'timeout': 100,
             'expr_form': 'list'},
            salt_api_url,
            {"X-Auth-Token": self.data.get("token_api_id")}
        )
        rst = code_pull.run()
        return rst

    def fetch(self):
        """执行"""
        code_checkout = salt_api_token(
            {'client': 'local',
             'fun': 'git.fetch',
             'tgt': self.data.get("tgt"),
             "arg": self.data.get("arg"),
             'timeout': 100,
             'expr_form': 'list'},
            salt_api_url,
            {"X-Auth-Token": self.data.get("token_api_id")}
        )
        rst = code_checkout.run()
        return rst
