import sys
import re

class Port() :
    TYPE_TERMINAL = 0
    TYPE_AGENT    = 1
    
    DIRECTION_SRC    = 0
    DIRECTION_DST    = 1

    def __init__(self, mac, ip, pnum=None, ptype=TYPE_TERMINAL, direction=None):
        self.pnum = pnum
        self.ip  = ip
        self.mac = mac
        self.ptype = ptype

        self.direction = direction

        if pnum is None :
            self.tag   = "dummy"
            self.label = ""
        else :
            self.tag   = "port{0}".format(pnum)
            self.label = "{0}".format(pnum)

        self.is_uplink = False

    def set_uplink(self, val) :
        self.is_uplink = val

    def set_pnum(self, val) :
        self.pnum = val

    def set_direction(self, val) :
        self.direction = val

    def to_dict(self):

        data = {
            "type": "port",
            "pnum": self.pnum,
            "ip": self.ip,
            "mac": self.mac,
            "ptype": self.ptype,
            "direction": self.direction,
            "is_uplink": self.is_uplink,
            "tag": self.tag,
            "label": self.label,
        }

        return data

