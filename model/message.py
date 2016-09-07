# coding: utf-8
__author__ = 'zheng'


class Message(object):

    def __init__(self, from_email=None, to_email=None, nickname=None, avatar=None, message=None, type=None):
        self.from_email = from_email
        self.to_email = to_email
        self.nickname = nickname
        self.avatar = avatar
        self.message = message
        self.type = type

    def to_json(self):
        return self.__dict__