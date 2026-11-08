import sys
import re

import logging
logger = logging.getLogger(__name__)

class Port() :

    def __init__(self, mac=None, ip=None):
        self.ip  = ip
        self.mac = mac

    def to_dict(self):

        data = {
            "ip": self.ip,
            "mac": self.mac,
        }

        return data

