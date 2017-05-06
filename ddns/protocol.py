from twisted.names import cache
from twisted.names.server import DNSServerFactory

from ddns.client import DynamicResolver


class DDNSFactory(DNSServerFactory):
    def __init__(self, redis_client, mongo_client, **kwargs):
        kwargs['clients'] = [DynamicResolver(redis_client, mongo_client)]
        DNSServerFactory.__init__(self, **kwargs)
