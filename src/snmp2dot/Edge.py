import sys
import re

import copy

import logging
logger = logging.getLogger(__name__)

DST_TYPE_TERMINAL = 0
DST_TYPE_AGENT = 1

class Edge() :
    #def __init__(self, src_ip, src_port, dst_mac, dst_ip, dst_port,
    #             is_src_port_uplink, is_available) :
    def __init__(self, src=None, dst=None, sport=None, dport=None, is_available=True) :
        self.src = src
        self.dst = dst

        self.indent = 1
        self.minlen = 5
        self.fp = sys.stdout

        self.sport = sport
        self.dport = dport

        self.is_available = is_available

        self.dst_type = DST_TYPE_TERMINAL

    def set_dst_type(dst_type) :
        self.dport.ptype = dst_type

    def to_dict(self):

        src = self.src
        dst = self.dst

        if self.dst_type == DST_TYPE_AGENT:
            src, dst = dst, src

        data = {
            "type": "edge",
            "src": src,
            "dst": dst,
            "minlen": self.minlen,
            "is_available": self.is_available,
        }

        return data
