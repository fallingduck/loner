# -*- coding: utf-8 -*-

import gevent
import time


def prune(cache):
    'Clean out expired records'

    while True:
        gevent.sleep(60)
        for record in dict(cache):
            if cache[record][1] < time.time():
                del cache[record]
