from twisted.names import dns, error
from twisted.internet import defer
from twisted.names.common import ResolverBase


class DynamicResolver(ResolverBase):
    REDIS_KEY_FORMAT = 'DDNS:{}:{}'

    def __init__(self, redis, mongo):
        """
        :param txredisapi.lazyConnectionPool redis: 
        :param ide.mongo.Database mongo:
        """
        self.redis = redis
        self.mongo = mongo
        self.ttl = 5
        ResolverBase.__init__(self)

    def _lookup(self, name, cls, type, timeout):
        return defer.fail(error.DNSQueryRefusedError())

    def lookupAddress(self, name, timeout=None):
        if isinstance(name, bytes):
            name = name.decode()

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

        d = defer.maybeDeferred(self._get_cached_a_record, name)
        d.addCallback(self._handle_cached_a_record, name)
        return d

    def _get_cached_a_record(self, name):
        rr_key = self.REDIS_KEY_FORMAT.format('A', name)
        return self.redis.get(rr_key)

    def _handle_cached_a_record(self, record, name, final=False):
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

        if final:
            return defer.fail(error.DNSNameError(name))

        d = defer.maybeDeferred(self._get_a_record, name)
        d.addCallback(self._handle_cached_a_record, name, True)

        return d

    @defer.inlineCallbacks
    def _get_a_record(self, name):
        """
        :param str name: 
        :return: 
        """
        reverse_name = name.split('.')
        reverse_name.reverse()
        query_key = 'rr.{}.A'.format('.'.join(reverse_name))
        query = {query_key: {'$exists': True}}
        cursor = yield self.mongo['rr_data'].find(query)

        final_domains = {}
        for doc in cursor:
            domain = doc.get('domain', 'example.com')
            if name.endswith(domain):
                final_domains[domain.count('.')] = doc

        def get_recurse(obj, key):
            if isinstance(key, str):
                key = key.split('.')
            value = obj
            for item in key:
                value = value.get(item)
                if not value:
                    break
            return value

        if final_domains:
            domain_doc = final_domains.get(max(final_domains.keys()))
            address = get_recurse(domain_doc, query_key)
            rr_key = self.REDIS_KEY_FORMAT.format('A', name)
            self.redis.set(rr_key, address)
            yield defer.returnValue(address)

        yield defer.fail(error.DNSNameError(name))
