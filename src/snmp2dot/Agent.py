import sys
import re

import copy

from . import Port

class Agent() :
    def __init__(self, uport, dports, imagepath, \
            logger=None, \
            minlen=4, \
            sysdescr=None, \
            sysobjectid=None, \
            ) :

        self.ip  = uport.ip
        self.mac = uport.mac
        self.indent = 1
        self.minlen = minlen

        self.dports = dports
        self.imagepath = imagepath

        self.uport = uport

        self.sysdescr = sysdescr
        self.sysobjectid= sysobjectid
        self.logger = logger
   
    def get_uport(self) :
        return self.uport

    def get_dports(self) :
        return self.dports

    def set_minlen(self, minlen) :
        self.minlen = minlen

    def print(self, fp) :
        indent = self.indent
        minlen = self.minlen

        agent_ip = self.ip
        agent_mac = self.mac
        uport    = self.uport
        dports = self.dports

        imagepath = self.imagepath
        
        if imagepath is None :
            imagepath = 'icons/doc_png/small_hub.png'

        lines = []
        cluster = re.sub(r'\.', '_', agent_ip)
        lines.append('subgraph cluster_{0} {{'.format(cluster))
        label = '{0}'.format(agent_ip)
        label += '\n{0}'.format(agent_mac)
        label += '\n{0}'.format(self.sysobjectid)
        lines.append('    label = "{0}";'.format(label))
        lines.append('')
        lines.append('    node_{0}_image ['.format(cluster))
        lines.append('        shape=none')
        lines.append('        image="{0}"'.format(imagepath))
        lines.append('        label=""')
        lines.append('        fixedsize=true')
        lines.append('        imagescale=height')
        lines.append('    ];'.format(cluster))
            
       
        lines.append('')
        # uplink port and downlink port
        for port in [ self.uport ] + self.dports:
            line  = '    '
            line += 'node_{0}_port{1} ['.format(cluster, port.pnum)
            line += '  shape=rectangle label="{0}"'.format(port.pnum)
            lines.append(line)
                    
            line  = '    '
            line += '  fixedsize=true'
            line += '  width=0.3 height=0.3 ];'
            lines.append(line)

        lines.append('')
        lines.append('    {')
        lines.append('        rank = same;')

        # downlink port only
        for port in dports:
             line  = '        '
             line += 'node_{0}_port{1};'.format(cluster, port.pnum)
             lines.append(line)
        
        lines.append('    }')
        lines.append('')

        color = 'none'

        src = 'node_{0}_port{1}'.format(cluster, uport.pnum)
        dst = 'node_{0}_image'.format(cluster)
    
        line  = '    '
        line += '{0} -> {1}'.format(src, dst)
        line += ' [color={0}]'.format(color)
        line += ';'
        lines.append(line)

        lines.append('')

        for port in dports:
            line  = '    '
            src = 'node_{0}_image'.format(cluster)
            dst = 'node_{0}_port{1}'.format(cluster, port.pnum)
            line += '{0} -> {1} [color={2}];'.format(src, dst, color)
            lines.append(line)
        
        lines.append('')
        src = None
        dst = None
        for port in dports:
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

