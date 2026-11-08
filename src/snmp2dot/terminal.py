import sys
import re

from .port import Port

class Terminal() :
    def __init__(self,
                 ip=None,
                 mac=None,
                 dport=None,
                 image=None,
                 is_src_port_uplink=None
        ) :

        self.ip = ip
        self.mac = mac

        self.indent = 1
        
        self.image = image
        self.is_src_port_uplink = is_src_port_uplink

        self.dport = dport
        self.sport = Port(None, None, None)

        self.port_order = 0

    def to_dict(self):

        image = self.image

        if image is None:
            image = "cisco/doc_png/pc.png"

        data = {
            "ip": self.ip,
            "mac": self.mac,
            "indent": self.indent,
            "image": self.image,
            "is_src_port_uplink": self.is_src_port_uplink,
            "dport": self.dport,
            "sport": self.sport,
            "port_order": self.port_order,
        }

        return data
