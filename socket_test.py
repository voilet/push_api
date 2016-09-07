#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
#     FileName: socket_test.py
#         Desc: 2015-15/1/7:下午12:21
#       Author: 苦咖啡
#        Email: voilet@qq.com
#     HomePage: http://blog.kukafei520.net
#      History: 
# =============================================================================
import json
from web_socket import web_socket_api
s = {'return': [{'122_30': {'cmd_|-production_service_|-cd /data/tmp; tar -xf OpenPlayCtrlService.tar.gz;dos2unix install.sh;/bin/sh install.sh;rm -rf /data/tmp/*; /etc/init.d/OpenPlayCtrlService start;_|-run': {'comment': 'Command "cd /data/tmp; tar -xf OpenPlayCtrlService.tar.gz;dos2unix install.sh;/bin/sh install.sh;rm -rf /data/tmp/*; /etc/init.d/OpenPlayCtrlService start;" run', 'name': 'cd /data/tmp; tar -xf OpenPlayCtrlService.tar.gz;dos2unix install.sh;/bin/sh install.sh;rm -rf /data/tmp/*; /etc/init.d/OpenPlayCtrlService start;', 'duration': 234, '__run_num__': 2, 'start_time': '12:42:19.945692', 'changes': {'pid': 12479, 'retcode': 0, 'stderr': "dos2unix: converting file install.sh to UNIX format ...\ndos2unix: converting file install.sh to UNIX format ...\nstandard in must be a tty\ntouch: cannot touch `/var/lock/subsys/OpenPlayCtrlService.pid': Permission denied", 'stdout': 'begin create work path\nstart to backup the OpenPlayCtrlService dir\ncreated a new backup: OpenPlayCtrlService-20150107124220.tar.gz\n/data/tmp\nOpenPlayCtrlService has installed successful\nStarting OpenPlayCtrlService: [FAILED]'}, 'result': True}, 'file_|-production_service_|-/data/tmp/OpenPlayCtrlService.tar.gz_|-managed': {'comment': 'File /data/tmp/OpenPlayCtrlService.tar.gz updated', 'name': '/data/tmp/OpenPlayCtrlService.tar.gz', 'duration': 497, '__run_num__': 1, 'start_time': '12:42:19.447482', 'changes': {'diff': 'New file', 'group': 'gamma', 'mode': '0644', 'user': 'gamma'}, 'result': True}, 'cmd_|-clear_open_data_|-rm -rf /data/tmp/*_|-run': {'comment': 'Command "rm -rf /data/tmp/*" run', 'name': 'rm -rf /data/tmp/*', 'duration': 7, '__run_num__': 0, 'start_time': '12:42:19.438994', 'changes': {'pid': 12458, 'retcode': 0, 'stderr': '', 'stdout': ''}, 'result': True}}}]}
# s = "%s" % (s)
web_socket_api(json.dumps(s))