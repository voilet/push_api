#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
#     FileName: web_socket.py
#         Desc: 2015-15/1/6:下午6:30
#       Author: 苦咖啡
#        Email: voilet@qq.com
#     HomePage: http://blog.kukafei520.net
#      History: 
# =============================================================================

from websocket import create_connection
import time
import json

# ws = create_connection("ws://127.0.0.1:8888/weebsocket/?jobs_id=r_220c3dbb05a1bae1e6ad0bec4a6ac331")
# while True:
ws = create_connection("ws://push-service.fun.tv/playcontrol/ws/pushsrv?mac=1c:a7:70:a8:0b:37&sn=142i96n68101037&fingerprint=Skyworth/SkyHi3751V800_A8H82/Hi3751V800:4.4.2/KOT49H/015.005.050:eng/test-keys&deviceId=1151&serialnum=unknown&androidid=ad9c1aec89b54c5c&board=bigfish&brand=Skyworth&cpuabi=armeabi-v7a&manufacturer=Skyworth+Inc.&modle=Skyworth+8H82+G8200&progduct=SkyHi3751V800_A8H82&versionrelease=4.4.2+HiDPTAndroid&versionsdk=19&densitydpi=240.0&density=1.5&widthpixels=1920&heightpixels=1080")
#ws.send(json.dumps({"data": "测试信息哦", "to_mail": "r_220c3dbb05a1bae1e6ad0bec4a6ac331"}))
result = ws.recv()
# time.sleep(2)
# print "Received '%s'" % result
ws.close()

