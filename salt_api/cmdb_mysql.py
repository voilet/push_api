#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
#     FileName: cmdb_mysql.py
#         Desc: 2015-15/1/28:下午5:29
#       Author: 苦咖啡
#        Email: voilet@qq.com
#     HomePage: http://blog.kukafei520.net
#      History: 
# =============================================================================

import MySQLdb
import json
def jobs_class(jid):
    db = MySQLdb.connect("192.168.115.205", "voilet", "wanghui", "fun_cmdb")
    cursor = db.cursor()
    test = "select id,success from salt_returns where jid=%s" % (jid)
    cursor.execute(test)
    rows = cursor.fetchall()
    row = dict(rows)
    db.close()
    return row

# s = jobs_class(20150115164022979374)
# for i in s:
#     print i