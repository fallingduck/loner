# -*- coding: utf-8 -*-

import gevent
from gevent import socket

import copy
import time

from dnslib import DNSRecord, RR

from config import config


nameservers = [(addr, 53) for addr in config['nameservers']]


def resolve(packet, cache={}):
    'Query every available nameserver, and attempt to unify the results'

    try:
        data = DNSRecord.parse(packet)

    except Exception:
        return ''  # The packet was formatted incorrectly, we can't do anything

    answer = cache_lookup(data, cache)  # Search the local cache first

    if answer:
        return answer.pack()

    results = []  # List of all the valid responses received
    errors = []   # List of all the errors from invalid responses

    # We now concurrently query all the nameservers we have listed
    gevent.joinall(
        [gevent.spawn(query_server, server, packet, results, errors)
            for server in nameservers],
        timeout=config['resolver']['request_timeout']
    )

    # If a majority of the servers didn't give us anything...
    if len(results) <= len(nameservers) // 2:

        answer = create_response(data)  # Construct an empty reply

        # We had some responses that were errors
        if len(errors):

            # Find the most common error
            error = max(set(errors), key=errors.count)
            answer.header.set_rcode(error)  # Reply with an error

        else:
            answer.header.set_rcode(3)  # Name Error

    else:

        # Find the most common answer
        reprs = [str(i) for i in results]
        result = max(results, key=lambda x: reprs.count(str(x)))

        # The most common result isn't agreed on by 50% of the servers
        if reprs.count(str(result)) <= len(results) // 2:
            answer = create_response(data)
            answer.header.set_rcode(3)

        else:

            # Everything actually checks out!
            answer = create_response(data)
            answer.add_answer(RR(data.q.qname, data.q.qtype, rdata=result))

            # Add the answer to the cache
            cache[(data.q.qname, data.q.qtype)] = (result,
                                                   (time.time() + data.a.ttl))

    return answer.pack()


def cache_lookup(data, cache):
    'Look in local cache to find a record'

    result = cache.get((data.q.qname, data.q.qtype))

    if result is None:
        return

    else:
        answer = create_response(data)
        answer.add_answer(RR(data.q.qname, data.q.qtype, rdata=result[0]))

    return answer


def query_server(server, packet, results, errors):
    'Query a DNS server'

    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    s.connect(server)

    s.send(packet)  # Forward the request to the nameserver

    # Q: Why would we ever get this big of a packet in return?
    # A: Because with IPv6, it's technically feasible
    response, addr = s.recvfrom(65535)

    try:
        data = DNSRecord.parse(response)  # Parse the response

    except Exception:
        return  # For some reason the packet was bad

    error = data.header.get_rcode()
    if error:
        errors.append(error)  # There was an error with the request
        return

    try:
        qtype = data.q.qtype
        answers = [i.rdata for i in data.rr if i.rtype == qtype]

        results.append(answers[0])  # Just add the first acceptable answer

    except IndexError:
        errors.append(3)


def create_response(query):
    'Create a response to match a query'
    response = copy.copy(query)
    response.header.set_qr(1)
    return query
