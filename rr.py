"""
rr.py

UDNS's DDNS cli

License: MIT
Copyright: 2017, Yehuda Deutsch <yeh@uda.co.il>
"""

from ConfigParser import ConfigParser
from argparse import ArgumentParser

import six
import txredisapi as redis
from twisted.internet import defer, reactor

parser = ArgumentParser('rr.py', 'Manage DDNS records')
parser.add_argument('--config', '-c', help='A config file for DDNS settings, default: ddns.ini', default='ddns.ini')
parser.add_argument('--zone', '-z', help='The zone (domain name) to add this record', required=True)
parser.add_argument('--host', '-o', help='The hostname to set the RR')
parser.add_argument('--type', '-t', help='The RR type, currently supports only A', default='A', choices=['A'])
parser.add_argument('--data', '-d', help='The data for the RR')

parser.add_argument('--list', '-l', help='Just list all records for zone', action='store_true')

args = parser.parse_args()

config = ConfigParser()
config.read(args.config)


@defer.inlineCallbacks
def rr_set():
    domain = args.zone.lower().strip()
    host = args.host.lower().strip()
    rr_type = args.type.upper().strip()
    data = args.data.strip()

    conn = yield redis.Connection(
        host=config.get('redis', 'host'),
        port=int(config.get('redis', 'port')),
        dbid=int(config.get('redis', 'db'))
    )

    hset = yield conn.hset(
        'DDNS:ZONE:{}'.format(domain),
        '{}:{}'.format(host, rr_type),
        data
    )

    if hset:
        print 'Set successful'
    else:
        print 'Update successful'

    yield conn.disconnect()


@defer.inlineCallbacks
def rr_get():
    domain = args.zone.lower().strip()
    host = args.host.lower().strip()
    rr_type = args.type.upper().strip()

    conn = yield redis.Connection(
        host=config.get('redis', 'host'),
        port=int(config.get('redis', 'port')),
        dbid=int(config.get('redis', 'db'))
    )

    data = yield conn.hget(
        'DDNS:ZONE:{}'.format(domain),
        '{}:{}'.format(host, rr_type)
    )

    print '{}.{}.\t{}\t{}'.format(host, domain, rr_type, data)

    yield conn.disconnect()


@defer.inlineCallbacks
def rr_list():
    domain = args.zone.lower().strip()

    conn = yield redis.Connection(
        host=config.get('redis', 'host'),
        port=int(config.get('redis', 'port')),
        dbid=int(config.get('redis', 'db'))
    )

    zone_rrs = yield conn.hgetall('DDNS:ZONE:{}'.format(domain))

    zone_hosts = ['{}\t{}\t{}'.format(*(key.split(':') + [value])) for key, value in six.iteritems(zone_rrs)]
    zone_hosts.sort()

    print '\n'.join(zone_hosts)

    yield conn.disconnect()


def main():
    cmd_method = rr_set
    if args.list:
        cmd_method = rr_list
    elif not args.data:
        cmd_method = rr_get
    cmd_method().addCallback(lambda ignore: reactor.stop())

if __name__ == '__main__':
    reactor.callWhenRunning(main)
    reactor.run()
