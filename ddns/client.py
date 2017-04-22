from twisted.names import dns, client


class DynamicResolver(client.Resolver):
    REDIS_KEY_FORMAT = 'DNS:{record}:'

    def __init__(self, redis):
        """
        :param txredis.client.RedisClient redis: 
        """
        self.redis = redis
        client.Resolver.__init__(self)

    def _get_rr(self, type):
        record = self.redis.get('')

    def lookupAddress(self, name, timeout=None):
        return ''
