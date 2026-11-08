import sys
import re

import copy

import logging
logger = logging.getLogger(__name__)

class Agent() :
    count = 0

    def __init__(self, 
            sysname="No sysname",
            ifaces=[],
            default_ifidx=None,
            uport=None, dports=[], image=None, 
            minlen=4, 
            sysdescr=None,
            sysobjectid=None,
            ) :

        self.sysname = sysname
        self.ifaces  = ifaces
        self.default_ifidx = default_ifidx

        self.indent = 1
        self.minlen = minlen

        self.dports = dports
        self.image = image

        self.uport = uport

        self.sysdescr = sysdescr
        self.sysobjectid= sysobjectid
   
    def get_uport(self) :
        return self.uport

    def get_dports(self) :
        return self.dports

    def set_minlen(self, minlen) :
        self.minlen = minlen

    def to_dict(self):
        data = {
            'sysname': self.sysname,
            'ifaces': self.ifaces,
            'default_ifidx': self.default_ifidx,
            'indent': self.indent,
            'minlen': self.minlen,
            'dports': self.dports,
            'image': self.image,
            'uport': self.uport,
            'sysdescr': self.sysdescr,
            'sysobjectid': self.sysobjectid,
        }

        return data
