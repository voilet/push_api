#!/usr/bin/env python
#-*- coding: utf-8 -*-
#=============================================================================
#     FileName: urls.py
#         Desc:
#       Author: 苦咖啡
#        Email: voilet@qq.com
#     HomePage: http://blog.kukafei520.net
#      Version: 0.0.1
#   LastChange: 2014 14-2-23 上午12:40
#      History: 
#=============================================================================


from chat.message import WebSocketHandler
# from index import MainHandler
from push import push_data, git_swan, git_shell, GitJava

handlers = [
    (r'^/swan_api/git/', git_swan),
    (r'^/swan_api/shell/', git_shell),
    (r'^/swan_api/java/', GitJava),
    (r'^/swan_api/', push_data),
    (r'^/websocket/$', WebSocketHandler),

]