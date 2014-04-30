# -*- coding: utf-8 -*-

import gevent
from gevent.server import DatagramServer

import resolver
import cleanup
from config import config


class Server(DatagramServer):
    'Receives incoming DNS packets, handles them concurrently'

    def handle(self, packet, address):
        'Handle an incoming DNS request'

        response = resolver.resolve(packet, cache)

        self.socket.sendto(response, address)


if __name__ == '__main__':
    print('Starting DNS server...')

    address = config['server']['address']
    print(('Listening at {0}'.format(address)))

    server = Server(address)

    cache = {}  # (name, type): (answer, expiration)
    cache_thread = gevent.spawn(cleanup.prune, cache)

    server.serve_forever()

    cache_thread.kill()
    print('Shutting down server...')
