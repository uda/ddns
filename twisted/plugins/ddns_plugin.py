from zope.interface import implementer

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet

from ddns.protocol import DDNSFactory


class Options(usage.Options):
    optParameters = [["port", "p", 5353, "The port number to listen on."]]


