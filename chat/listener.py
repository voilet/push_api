# coding:utf-8
import json
import threading
from tornado.log import app_log
from chat.manager import ClientManager


class Listener(threading.Thread):

    def __init__(self, r, channels):
        threading.Thread.__init__(self)
        self.redis = r
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channels)

    def work(self, item):

        """
        @param item: redis 消息对象
        """

        data = item['data']
        if data == 1L:
            return
        app_log.info(data)
        try:

            data = json.loads(data)
            print data
            if data.get('to_email') != 'groups':
                ClientManager.send_to(data.get('to_email'), data)
            else:
                ClientManager.send_to_all(data)
        except Exception as ex:
            app_log.exception(ex)

    def run(self):
        for item in self.pubsub.listen():
            if item['data'] == "KILL":
                self.pubsub.unsubscribe()
                break
            else:
                self.work(item)

