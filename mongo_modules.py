#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
#     FileName: mongo_modules.py
#         Desc: 2015-15/1/5:下午2:10
#       Author: 苦咖啡
#        Email: voilet@qq.com
#     HomePage: http://blog.kukafei520.net
#      History: 
# =============================================================================

from mongoengine import *
from datetime import datetime

class mongo_swan(Document):
    project_name = StringField(max_length=50, required=True)
    swan_name = StringField()
    project_id = IntField()
    choose = IntField()
    salt_sls = StringField()
    config_name = StringField()
    check_port_status = BooleanField()
    check_port = StringField()
    bat_push = BooleanField()
    script = StringField()
    tgt = StringField()
    argall_str = StringField()
    datetime = DateTimeField(default=datetime.now())