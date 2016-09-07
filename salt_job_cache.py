#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
#     FileName: salt_job_cache.py
#         Desc: 2015-15/4/8:下午2:10
#       Author: 苦咖啡
#        Email: voilet@qq.com
#     HomePage: http://blog.kukafei520.net
#      History: 
# =============================================================================

#!/bin/env python
#coding=utf8

# Import python libs
import json
import redis
# Import salt modules
import salt.config
import salt.utils.event
from salt.output import display_output
opts={'extension_modules': '/var/cache/salt/master/extmods',
          'color': False,
          'state_verbose': True,
    }
# Import third party libs
# import MySQLdb

__opts__ = salt.config.client_config('/etc/salt/master')

# redis key pubsub
rc = redis.Redis(host='192.168.111.101',port=6379,db=1)
# ps = r.pubsub()

# Listen Salt Master Event System
event = salt.utils.event.MasterEvent(__opts__['sock_dir'])
for eachevent in event.iter_events(full=True):
    ret = eachevent['data']
    #print ret
    if "salt/job/" in eachevent['tag']:
        # Return Event
        print ret
        print ret.has_key('id')
        if ret.has_key('id') and ret.has_key('return'):
            # Igonre saltutil.find_job event
            if ret['fun'] == "saltutil.find_job":
                continue
            print "*" * 50
            display_output(ret["return"], "highstate", opts=opts)
            print json.dumps(ret["return"])
            #r_sub_key = "%s" %(ret['jid'])
            #ps = rc.pubsub()
            #ps.subscribe("web_chat")
            #rc.publish("web_chat", json.dumps({"message": ret["return"], "to_email": r_sub_key, "id": ret["id"]}))
            #print "redis is ok"
    # Other Event
    else:
        pass