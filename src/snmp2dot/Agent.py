import sys
import re

import copy

from . import Port

import logging
logger = logging.getLogger(__name__)

class Agent() :
    count = 0

    def __init__(self, 
            sysname="No sysname",
            ifaces=[],
            default_ifidx=None,
            uport=None, dports=[], imagepath=None, 
            logger=None,
            minlen=4, 
            sysdescr=None,
            sysobjectid=None,
            ) :

        self.sysname = sysname
        self.ifaces  = ifaces
        self.default_ifidx = default_ifidx

        #self.ip  = uport.ip
        #self.mac = uport.mac
        self.indent = 1
        self.minlen = minlen

        self.dports = dports
        self.imagepath = imagepath

        self.uport = uport

        self.sysdescr = sysdescr
        self.sysobjectid= sysobjectid
   
    def get_uport(self) :
        return self.uport

    def get_dports(self) :
        return self.dports

    def set_minlen(self, minlen) :
        self.minlen = minlen

    def print(self, fp) :
        indent = self.indent
        minlen = self.minlen

        #agent_ip = self.ip
        #agent_mac = self.mac
        #uport    = self.uport
        #dports = self.dports

        imagepath = self.imagepath
        
        if imagepath is None :
            imagepath = 'icons/doc_png/small_hub.png'

        sysname = re.sub(r'\.', '_', self.sysname)

        lines = []
        #cluster = re.sub(r'\.', '_', agent_ip)
        lines.append('// count is {0}'.format(Agent.count))
        Agent.count = Agent.count + 1

        lines.append('subgraph cluster_{0} {{'.format(sysname))
        #label = '{0}'.format(agent_ip)
        #label += '\n{0}'.format(agent_mac)
        #label += '\n{0}'.format(self.sysobjectid)

        label = self.sysname

        lines.append('    label = "{0}";'.format(label))
        lines.append('')
        lines.append('    node_{0}_image ['.format(sysname))
        lines.append('        shape=none')
        lines.append('        image="{0}"'.format(imagepath))
        lines.append('        label=""')
        lines.append('        fixedsize=true')
        lines.append('        imagescale=height')
        lines.append('    ];')
            
       
        lines.append('')

        line = '    // uplink port and downlink port'
        lines.append(line)

        for ifid in self.ifaces :
            name = 'node_{0}_port{1}'.format(sysname, ifid)
            
            line  = '    '
            line += '{0} ['.format(name)
            line += '  shape=rectangle label="{0}"'.format(ifid)
            lines.append(line)
                
            line  = '    '
            line += '  fixedsize=true'
            line += '  width=0.3 height=0.3 ];'
            lines.append(line)
            line += ''


        lines.append('')
        lines.append('    {')
        lines.append('        // grouping downlink port')
        lines.append('        rank = same;')
        
        for ifid in self.ifaces :
            if int(ifid) == int(self.default_ifidx) :
                # ignore uplink port
                continue

            line  = '        '
            line += 'node_{0}_port{1};'.format(sysname, ifid)
            lines.append(line)

        lines.append('    }')
        lines.append('')

        color = 'red'
        
        line  = '    // uplink port -> node_image'
        lines.append(line)

        src = 'node_{0}_port{1}'.format(sysname, self.default_ifidx)
        dst = 'node_{0}_image'.format(sysname)
    
        line  = '    '
        line += '{0} -> {1}'.format(src, dst)
        line += ' [color={0}]'.format(color)
        line += ';'
        lines.append(line)

        lines.append('')


        color = 'blue'
        line  = '    // node_image -> downlink port'
        lines.append(line)
        for ifid in self.ifaces :
            if int(ifid) == int(self.default_ifidx) :
                # ignore uplink port
                continue

            line  = '    '
            src = 'node_{0}_image'.format(sysname)
            dst = 'node_{0}_port{1}'.format(sysname, ifid)
            line += '{0} -> {1} [color={2}];'.format(src, dst, color)
            lines.append(line)
        
        lines.append('')

        src = None
        dst = None
        for port in self.dports:
            dst = port.pnum
            if src is None:
                src = dst
                continue

            line  = '    '
            line += 'node_{0}_port{1} -> node_{0}_port{2} [color=none,minlen={3}];'.format(cluster, src, dst, minlen)
            lines.append(line)
            src = dst

        lines.append('    // end of subgraph')
        # end of subgraph
        lines.append('}')

        for line in lines :
            fp.write(' ' * indent * 4)
            fp.write(line)
            fp.write('\n')
        fp.write('\n')

