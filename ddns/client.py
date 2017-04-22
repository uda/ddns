import random

import six
from twisted.names import dns, error
from twisted.internet import defer
from twisted.names.common import ResolverBase


class DynamicResolver(ResolverBase):
    REDIS_KEY_FORMAT = 'DDNS:ZONE:{}'
    REDIS_FIELD_FORMAT = '{}:{}'

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
            if isinstance(record, six.string_types):
                record = record.strip()
                if '\x1e' in record:
                    record = random.choice(record.split('\x1e'))
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
        host, domain = name.split('.', 1)
        rr_key = self.REDIS_KEY_FORMAT.format(domain)
        rr_field = self.REDIS_FIELD_FORMAT.format(host, 'A')
        return self.redis.hget(rr_key, rr_field)
