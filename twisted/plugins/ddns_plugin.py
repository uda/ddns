from ConfigParser import ConfigParser

import txredisapi
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
            host=config.get('redis', 'host'),
            port=int(config.get('redis', 'port')),
            dbid=int(config.get('redis', 'db'))
        )

        dns_factory = DDNSFactory(redis_client)

        application = service.Application('ddns')
        service_collection = service.IServiceCollection(application)

        internet.TCPServer(dns_port, dns_factory).setServiceParent(service_collection)
        internet.UDPServer(dns_port, dns.DNSDatagramProtocol(dns_factory)).setServiceParent(service_collection)

        return service_collection

serviceMaker = DDNSServiceMaker()
