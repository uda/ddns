from twisted.names import dns, error
from twisted.internet import defer
from twisted.names.common import ResolverBase


class DynamicResolver(ResolverBase):
    REDIS_KEY_FORMAT = 'DDNS:{}:{}'

    def __init__(self, redis):
        """
        :param txredisapi.lazyConnectionPool redis: 
        """
        self.redis = redis
        self.ttl = 5
        ResolverBase.__init__(self)

    def _lookup(self, name, cls, type, timeout):
        return defer.fail(error.DNSQueryRefusedError())

    def lookupAddress(self, name, timeout=None):
        def return_record(record):
            if record:
                return defer.succeed([
                    (dns.RRHeader(
                        name=name,
                        ttl=self.ttl,
                        payload=dns.Record_A(record, self.ttl),
                        auth=True
                    ),),
                    (),
                    ()
                ])
            else:
                return defer.fail(error.DNSNameError(name))

        d = defer.maybeDeferred(self._get_a_record, name)
        d.addCallback(return_record)
        return d

    def _get_a_record(self, name):
        rr_key = self.REDIS_KEY_FORMAT.format('A', name)
        return self.redis.get(rr_key)
