import sys
import re

from snmp2dot.Port import Port

class Terminal() :
    def __init__(self, dport, imagepath, is_src_port_uplink) :
        self.indent = 1
        
        self.imagepath = imagepath
        self.is_src_port_uplink = is_src_port_uplink

        self.dport = dport
        self.sport = Port(None, None, None)

        self.port_order = 0

    def print(self, fp) :
        imagepath = self.imagepath
        dport = self.dport

        # usually dummy port
        sport = self.sport

        lines = []
        if dport.ip :
            label = dport.ip + '\n' + dport.mac
            cluster = re.sub(r'\.', '_', dport.ip)
        else :
            label = dport.mac
            cluster = re.sub(r'\:', '_', dport.mac)

        if imagepath is None : 
            imagepath='icons/doc_jpg/pc.png'

        lines.append('subgraph cluster_{0} {{'.format(cluster))
        lines.append('    label = "{0}";'.format(label))
        lines.append('    node_{0}_image ['.format(cluster))
        lines.append('        shape=none')
        lines.append('        image="{0}"'.format(imagepath))
        lines.append('        label=""')
        lines.append('        fixedsize=true')
        lines.append('        imagescale=width')
        lines.append('    ];'.format(cluster))
        lines.append('    node_{0}_{1} ['.format(cluster, dport.tag))
        lines.append('        shape=box')
        lines.append('        label="{0}"'.format(dport.label))
        lines.append('        fixedsize=true')
        lines.append('        width=0.3')
        lines.append('        height=0.3')
        lines.append('    ];')

        lines.append('    node_{0}_{1} ['.format(cluster, sport.tag))
        lines.append('        style=invisible')
        lines.append('        shape=box')
        lines.append('        label="{0}"'.format(sport.label))
        lines.append('        fixedsize=true')
        lines.append('        width=0.3')
        lines.append('        height=0.3')
        lines.append('    ];')

        if self.port_order == 0 :
            lines.append('    node_{0}_{1} -> node_{0}_image [color=none, weight=100, len=0.3];'.format(cluster, dport.tag))
            lines.append('    node_{0}_image -> node_{0}_{1} [color=none ];'.format(cluster, sport.tag))
        else :
            lines.append('    node_{0}_{1} -> node_{0}_image [color=none, weight=100, len=0.3];'.format(cluster, sport.tag))
            lines.append('    node_{0}_image -> node_{0}_{1} [color=none ];'.format(cluster, dport.tag))

        lines.append('};')

        indent = ' ' * self.indent * 4
        for line in lines :
            fp.write("{0}{1}".format(indent, line))
            fp.write('\n')
        fp.write('\n')

