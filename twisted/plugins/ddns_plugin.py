from configparser import ConfigParser

import txredisapi
import txmongo
from twisted.names import dns
from zope.interface import implementer

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet, service

from ddns.protocol import DDNSFactory


class Options(usage.Options):
    optParameters = [
        ['port', 'p', 53, 'The port number to listen on.'],
        ['config', 'c', 'ddns.ini', 'A INI config file.'],
    ]


@implementer(IServiceMaker, IPlugin)
class DDNSServiceMaker(object):
    tapname = 'ddns'
    description = 'Quick DDNS using redis'
    options = Options

    def makeService(self, options):
        config = ConfigParser()
        config.read(options['config'])

        dns_port = int(config.get('dns', 'port') or options['port'])

        redis_client = txredisapi.lazyConnectionPool(
            host=config.get('redis', 'host', fallback='127.0.0.1'),
            port=int(config.get('redis', 'port', fallback=6379)),
            dbid=int(config.get('redis', 'db', fallback=0)),
        )

        mongo_client = txmongo.lazyMongoConnectionPool(
            host=config.get('mongo', 'host', fallback='127.0.0.1'),
            port=int(config.get('mongo', 'port', fallback=27017)),
        )

        dns_factory = DDNSFactory(redis_client, mongo_client['ddns'])

        application = service.Application('ddns')
        service_collection = service.IServiceCollection(application)

        internet.TCPServer(dns_port, dns_factory).setServiceParent(service_collection)
        internet.UDPServer(dns_port, dns.DNSDatagramProtocol(dns_factory)).setServiceParent(service_collection)

        return service_collection

serviceMaker = DDNSServiceMaker()
