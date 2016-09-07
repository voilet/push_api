# coding: utf-8



class Client():

    def __init__(self, identity, jid='', handler=None):
        self._identity = identity
        self._handler = handler
        self._jid = jid

    @property
    def identity(self):
        identity = str(id(self._handler))
        return identity

    @property
    def handler(self):
        return self._handler

    # @property
    # def nickname(self):
    #     return self._nickname

    @property
    def email(self):
        return self._jid

    @property
    def avatar(self):
        return "none"
        # return Gavatar(self._email).get_default_avatar()

    def __str__(self):
        return self.identity
