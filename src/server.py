# -*- coding: utf-8 -*-

from gevent.server import DatagramServer

import resolver
from config import config


class Server(DatagramServer):
    'Receives incoming DNS packets, handles them concurrently'

    def handle(self, packet, address):
        'Handle an incoming DNS request'

        response = resolver.resolve(packet)  # Hand the request to the resolver

        self.socket.sendto(response, address)  # Send back the response


if __name__ == '__main__':
    print('Starting DNS server...')
    address = config['server']['address']
    print(('Listening at {0}'.format(address)))
    server = Server(address)
    server.serve_forever()
    print('Shutting down server...')
