# coding: utf-8
from chat.util.gavatar import Gavatar


class Client():

    def __init__(self, identity, nickname="", email='', handler=None):
        self._identity = identity
        self._handler = handler
        self._nickname = nickname
        self._email = email

    @property
    def identity(self):
        identity = str(id(self._handler))
        return identity

    @property
    def handler(self):
        return self._handler

    @property
    def nickname(self):
        return self._nickname

    @property
    def email(self):
        return self._email

    @property
    def avatar(self):
        return Gavatar(self._email).get_default_avatar()

    def __str__(self):
        return self.identity
