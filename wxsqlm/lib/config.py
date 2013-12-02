# -*- coding: utf-8 -*-

__author__ = 'Mehmet Öztürk'

import json
import sqlmap


def get_conf():
    with open(sqlmap.modulePath()+'/wxsqlm/config.json', 'r') as r:
        conf = json.loads(r.read())
    return conf
