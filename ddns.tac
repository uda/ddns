import pathlib
import tomllib

import txredisapi
from twisted.application import service, internet
from twisted.names import dns

from txddns.protocol import DDNSFactory


def create_application():
    _application = service.Application("ddns")
    _collection = service.IServiceCollection(_application)

    config = tomllib.loads(pathlib.Path("ddns.toml").read_text())

    dns_port = int(config.get("dns", {}).get("port") or 53)
    redis_config = config.get("redis", {})

    redis_client = txredisapi.lazyConnectionPool(
        host=str(redis_config.get("host", "127.0.0.1")),
        port=int(redis_config.get("port", 6379)),
        dbid=int(redis_config.get("db", 0)),
    )

    ddns_factory = DDNSFactory(redis_client)

    internet.TCPServer(dns_port, ddns_factory).setServiceParent(_collection)
    internet.UDPServer(dns_port, dns.DNSDatagramProtocol(ddns_factory)).setServiceParent(_collection)

    return _application


application = create_application()
