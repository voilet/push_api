#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
#     FileName: test_mongo.py
#         Desc: 2014-14/12/31:下午1:51
#       Author: 苦咖啡
#        Email: voilet@qq.com
#     HomePage: http://blog.kukafei520.net
#      History: 
# =============================================================================

from mongoengine import *

class shop_locations(Document):
    shop_id = IntField()
    shop_name = StringField()
    activated = StringField()
    address = StringField()
    category = StringField()
    lng = StringField()
    lat = StringField()
    location = ListField(FloatField())

if __name__ == '__main__':
    # 连接shop_locations库
    connect('config_center')
    # shop_id为1的记录是否存在，不存在则创建，存在则打印出地址
    try:
        sl = shop_locations.objects.get(shop_id=1)
    except shop_locations.DoesNotExist:
        sl = shop_locations()
        sl.shop_id = 1
        sl.shop_name = 'Starbucks'
        sl.activated = 'Y'
        sl.address = '921, Whitehorse Road, Box Hill,Melbourne,3128, Victoria, Australia'
        sl.category = 'cafe'
        sl.lng = '145.1225427'
        sl.lat = '-37.8181463'
        sl.location = [145.1225427, -37.8181463]
        sl.save()
    else:
        print sl.address
        print sl.shop_name
        print sl.category