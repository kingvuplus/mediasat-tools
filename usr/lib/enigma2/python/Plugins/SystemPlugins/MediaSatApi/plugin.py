from Plugins.Plugin import PluginDescriptor
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from MediaSat.MeInterface import MediaSatInterface
import socket
DeliteInt = None

class Deliteapi(Protocol):

    def connectionMade(self):
        self.received = ''

    def dataReceived(self, data):
        self.received += data

    def connectionLost(self, reason):
        global DeliteInt
        data = self.received
        i = data.find('\x00')
        if i != -1:
            data = data[0:i]
        print 'BlackHoleapi:', data
        DeliteInt.procCmd(data)


def sessionstart(reason, session):
    DeliteInt.setSession(session)


def autostart(reason, **kwargs):
    global DeliteInt
    if reason == 0:
        DeliteInt = MediaSatInterface()
        print 'starting BlackHoleapi handler'
        factory = Factory()
        factory.protocol = Deliteapi
        try:
            import os
            os.remove('/tmp/Meapi.socket')
        except OSError:
            pass

        reactor.listenUNIX('/tmp/Meapi.socket', factory)
        mydata = 'START_CAMD'
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client_socket.connect('/tmp/Blackhole.socket')
        client_socket.send(mydata)
        client_socket.close()


def Plugins(**kwargs):
    return [PluginDescriptor(name='MediaSatApi', description='MediaSat image Api', where=PluginDescriptor.WHERE_SESSIONSTART, fnc=sessionstart), PluginDescriptor(where=PluginDescriptor.WHERE_AUTOSTART, fnc=autostart)]