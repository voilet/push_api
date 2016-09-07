#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    FileName: check_api.py
        Desc:
      Author: 苦咖啡
       Email: voilet@qq.com
    HomePage: http://blog.kukafei520.net
     Version: 0.0.1
  LastChange: 16/1/4 下午3:21
     History:   
"""

import requests


class CheckApi(object):
    """pxe api接口"""

    def __init__(self, **kwargs):
        self.data = kwargs
        self.headers = {
            'CustomUser-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
        }
        self.proxies = {
            "http": "%s:80" % self.data.get("ip"),
        }

    def run(self):
        """执行"""
        try:
            result = requests.get(self.data.get("url"), headers=self.headers, proxies=self.proxies, timeout=10)
        except requests.exceptions.ConnectTimeout, e:
            print e
            print u"请求超时"
            return False, u"接口请求超时"
        except requests.TooManyRedirects, e:
            print e
            return False, u"接口过多重定向"
        except requests.ConnectionError, e:
            print e
            return False, u"连接错误"
        try:
            rst = result.json()
            if int(rst.get("retCode")) == 200:
                return True, rst.get("retMsg", "no message")
            else:
                return False, rst.get("retMsg", "no message")
        except:
            return False, "数据格式错误"


if __name__ == '__main__':
    s = CheckApi(url="http://js.tv.funshion.com/search/vretrieve/v1?vtype=1026&cate=196&order=3", ip="192.168.111.5")
    print s.run()
