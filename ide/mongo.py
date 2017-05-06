from txmongo import connection, database, collection


class Collection(collection.Collection):
    def __getattr__(self, name):
        """
        :param str name:
        :rtype: Collection
        """
        return super(Collection, self).__getattr__(name)

    def __getitem__(self, name):
        """
        :param str name:
        :rtype: Collection
        """
        return super(Collection, self).__getitem__(name)


class Database(database.Database):
    def __getattr__(self, name):
        """
        :param str name:
        :rtype: Collection
        """
        return super(Database, self).__getattr__(name)

    def __getitem__(self, name):
        """
        :param str name:
        :rtype: Collection
        """
        return super(Database, self).__getitem__(name)


class ConnectionPool(connection.ConnectionPool):
    def __getattr__(self, name):
        """
        :param str name:
        :rtype: Database
        """
        return super(ConnectionPool, self).__getattr__(name)

    def __getitem__(self, name):
        """
        :param str name:
        :rtype: Database
        """
        return super(ConnectionPool, self).__getitem__(name)


class MongoConnection(ConnectionPool):
    pass


class MongoConnectionPool(ConnectionPool):
    pass


class lazyMongoConnection(ConnectionPool):
    pass


class lazyMongoConnectionPool(ConnectionPool):
    pass
