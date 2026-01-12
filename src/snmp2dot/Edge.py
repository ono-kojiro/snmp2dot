import sys
import re

import copy

DST_TYPE_TERMINAL = 0
DST_TYPE_AGENT = 1

class Edge() :
    #def __init__(self, src_ip, src_port, dst_mac, dst_ip, dst_port,
    #             is_src_port_uplink, is_available) :
    def __init__(self, sport, dport, is_available) :

        self.indent = 1
        self.minlen = 5
        self.fp = sys.stdout

        self.sport = sport
        self.dport = dport

        self.is_available = is_available

        self.dst_type = DST_TYPE_TERMINAL

    def set_dst_type(dst_type) :
        self.dport.ptype = dst_type

    def print(self, fp) :
        src = str(self.sport)
        dst = str(self.dport)

        portpos = 'e' # east

        line  = ' ' * self.indent * 4
        if self.dst_type == DST_TYPE_AGENT :
            tmp = src
            src = dst
            dst = tmp

        line += '"{0}":{1} -> "{2}"'.format(src, portpos, dst)
        if self.minlen :
            line += ' [minlen={0}]'.format(self.minlen)
        line += ';'

        if self.is_available :
            fp.write(line + '\n')


