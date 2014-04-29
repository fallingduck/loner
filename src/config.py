# -*- coding: utf-8 -*-

import yaml


with open('/etc/loner.conf', 'r') as f:
    config = yaml.load(f)
