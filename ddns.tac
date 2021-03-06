import txredisapi
from twisted.application import service, internet
from twisted.names import dns
from ConfigParser import ConfigParser

from ddns.protocol import DDNSFactory


def create_application():
    _application = service.Application('ddns')
    _collection = service.IServiceCollection(application)

    config = ConfigParser()
    config.read('ddns.ini')

    dns_port = int(config.get('dns', 'port') or 53)

    redis_client = txredisapi.lazyConnectionPool(
        host=config.get('redis', 'host'),
        port=config.get('redis', 'port'),
        dbid=config.get('redis', 'db')
    )

    ddns_factory = DDNSFactory(redis_client)

    internet.TCPServer(dns_port, ddns_factory).setServiceParent(_collection)
    internet.UDPServer(dns_port, dns.DNSDatagramProtocol(ddns_factory)).setServiceParent(_collection)

    return _application

application = create_application()
