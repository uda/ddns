import pathlib
import tomllib

import txredisapi
from twisted.application import internet, service
from twisted.application.service import IServiceMaker
from twisted.names import dns
from twisted.plugin import IPlugin
from twisted.python import usage
from zope.interface import implementer

from txddns.protocol import DDNSFactory


class Options(usage.Options):
    optParameters = [
        ["listen", "l", None, "The port number to listen on."],
        ["config", "c", "ddns.toml", "A INI config file."],
        ["redis-host", "h", None, "The redis hostname"],
        ["redis-port", "p", None, "The redis port"],
        ["redis-db", "d", None, "The redis database ID"],
    ]


@implementer(IServiceMaker, IPlugin)
class DDNSServiceMaker(object):
    tapname = "ddns"
    description = "Quick DDNS using redis"
    options = Options

    def makeService(self, options):
        config = tomllib.loads(pathlib.Path(options["config"]).read_text())

        dns_port = int(options["listen"] or config.get("dns", {}).get("port", 53))
        redis_config = config.get("redis", {})

        redis_client = txredisapi.lazyConnectionPool(
            host=str(options["redis-host"] or redis_config.get("host", "127.0.0.1")),
            port=int(options["redis-port"] or redis_config.get("port", 6379)),
            dbid=int(options["redis-db"] or redis_config.get("db", 0)),
        )

        dns_factory = DDNSFactory(redis_client)

        application = service.Application("ddns")
        service_collection = service.IServiceCollection(application)

        internet.TCPServer(dns_port, dns_factory).setServiceParent(service_collection)
        internet.UDPServer(dns_port, dns.DNSDatagramProtocol(dns_factory)).setServiceParent(service_collection)

        return service_collection


serviceMaker = DDNSServiceMaker()
