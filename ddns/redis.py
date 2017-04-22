from twisted.internet import protocol, reactor
from txredis.client import RedisClient


class Redis(object):
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)

    def get_client(self):
        client_creator = protocol.ClientCreator(reactor, RedisClient)
        redis = yield client_creator.connectTCP(self.host, self.port)
