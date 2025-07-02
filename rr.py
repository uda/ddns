"""
rr.py

UDNS's DDNS cli

License: MIT
Copyright: 2025, Yehuda Deutsch <yeh@uda.co.il>
"""
import enum

import txredisapi as redis
import typer
from twisted.internet import defer, reactor
from typing_extensions import Annotated

cli = typer.Typer()


class RRCommand:
    def __init__(self, host: str = "127.0.0.1", port: int = 6379, dbid: int = 0):
        self.host = str(host)
        self.port = int(port)
        self.dbid = int(dbid)
        self.conn: redis.Connection = None

        self.d = defer.Deferred()

    def run(self, command: callable, *args):
        def exec():
            d = self.connect()
            d.addErrback(self.disconnect)
            d.addCallback(command, *args)
            d.addBoth(self.disconnect)
            return d

        reactor.callWhenRunning(exec)
        reactor.run()

    @defer.inlineCallbacks
    def connect(self):
        self.conn = yield redis.Connection(host=self.host, port=self.port, dbid=self.dbid)

    @defer.inlineCallbacks
    def disconnect(self, result):
        if self.conn:
            yield self.conn.disconnect()
        reactor.stop()

    @defer.inlineCallbacks
    def rr_set(self, conn, zone: str, host: str, rr_type: str, data: str):
        hset = yield self.conn.hset(f"DDNS:ZONE:{zone}", f"{host}:{rr_type}", data)
        if hset:
            typer.echo(f"Record set successfully for {host}:{rr_type}: {data}")
        else:
            typer.echo(f"Record set failed for {host}:{rr_type}: {data}")

    @defer.inlineCallbacks
    def rr_get(self, conn, zone: str, host: str, rr_type: str):
        data = yield self.conn.hget(f"DDNS:ZONE:{zone}", f"{host}:{rr_type}")
        typer.echo(f"{host}.{zone}.\t{rr_type}\t{data}")

    @defer.inlineCallbacks
    def rr_delete(self, conn, zone: str, host: str, rr_type: str):
        hdel = yield self.conn.hdel(f"DDNS:ZONE:{zone}", f"{host}:{rr_type}")
        if hdel:
            typer.echo(f"Record delete successfully for {host}:{rr_type}")
        else:
            typer.echo(f"Record delete failed for {host}:{rr_type}")

    @defer.inlineCallbacks
    def rr_list(self, conn, zone: str):
        zone_rr_list = yield self.conn.hgetall(f"DDNS:ZONE:{zone}")
        typer.echo("Got all records")
        typer.echo(f"Zone: {zone}")
        typer.echo("\n".join(sorted([
            "{}\t{}\t{}".format(*(key.split(":") + [value]))
            for key, value in zone_rr_list.items()
        ])))


class RRType(enum.StrEnum):
    A = "A"


def to_lower(value: str):
    return value.lower()


@cli.command(name="set")
def rr_set(
        zone: Annotated[str, typer.Option(parser=to_lower)],
        host: Annotated[str, typer.Option(parser=to_lower)],
        rr_type: Annotated[RRType, typer.Option(case_sensitive=False)],
        data: Annotated[str, typer.Option()],
):
    rr_cmd = RRCommand()
    rr_cmd.run(rr_cmd.rr_set, zone, host, rr_type, data)


@cli.command(name="get")
def rr_get(
        zone: Annotated[str, typer.Option(parser=to_lower)],
        host: Annotated[str, typer.Option(parser=to_lower)],
        rr_type: Annotated[RRType, typer.Option(case_sensitive=False)],
):
    rr_cmd = RRCommand()
    rr_cmd.run(rr_cmd.rr_get, zone, host, rr_type)


@cli.command(name="delete")
def rr_delete(
        zone: Annotated[str, typer.Option(parser=to_lower)],
        host: Annotated[str, typer.Option(parser=to_lower)],
        rr_type: Annotated[RRType, typer.Option(case_sensitive=False)],
):
    rr_cmd = RRCommand()
    rr_cmd.run(rr_cmd.rr_delete, zone, host, rr_type)


@cli.command(name="list")
def rr_list(zone: Annotated[str, typer.Option(parser=to_lower)]):
    rr_cmd = RRCommand()
    rr_cmd.run(rr_cmd.rr_list, zone)


if __name__ == '__main__':
    cli()
