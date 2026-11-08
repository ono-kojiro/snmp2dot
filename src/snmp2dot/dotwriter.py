import re

import logging
logger = logging.getLogger(__name__)

from pprint import pprint

class DotWriter:

    def __init__(self, fp):
        self.fp = fp

    def write_edge(self, data):

        if not data["is_available"]:
            return

        line = f'"{data["src"]}":e -> "{data["dst"]}"'

        if data["minlen"]:
            line += f' [minlen={data["minlen"]}]'

        line += ';'

        self.fp.write(line)
        self.fp.write("\n")

    def port_name(self, port):

        if port["ip"]:
            cluster = port["ip"]
        else:
            cluster = port["mac"]

        cluster = re.sub(r'[.:]', '_', cluster)

        return f'node_{cluster}_port{port["pnum"]}'

    def write_terminal(self, data):
        dport = data.get('dport')

        # usually dummy port
        sport = data.get('sport')

        lines = []
        #if dport.ip :
        #    label = dport.ip + '\n' + dport.mac
        #    cluster = re.sub(r'\.', '_', dport.ip)
        #else :
        #    label = dport.mac
        #    cluster = re.sub(r'\:', '_', dport.mac)

        label = data.get('mac')
        name = re.sub(r'\:', '_', data['mac'])

        image = 'cisco/doc_png/pc.png'

        lines.append('subgraph cluster_{0} {{'.format(name))
        lines.append('    label = "{0}";'.format(label))
        lines.append('    node_{0}_image ['.format(name))
        lines.append('        shape=none')
        lines.append('        image="{0}"'.format(image))
        lines.append('        label=""')
        lines.append('        fixedsize=true')
        lines.append('        imagescale=width')
        lines.append('    ];')
        lines.append('    node_{0}_port1 ['.format(name))
        lines.append('        shape=box')
        lines.append('        label="1"')
        lines.append('        fixedsize=true')
        lines.append('        width=0.3')
        lines.append('        height=0.3')
        lines.append('    ];')

        lines.append('    node_{0}_dummy ['.format(name))
        #lines.append('        style=invisible')
        lines.append('        shape=box')
        lines.append('        label="d"')
        lines.append('        fixedsize=true')
        lines.append('        width=0.3')
        lines.append('        height=0.3')
        lines.append('    ];')

        attrs = 'color=gray, weight=100, len=0.3'
        lines.append('    node_{0}_port1 -> node_{0}_image [ {1} ];'.format(name, attrs))
        attrs = 'color=gray, weight=100, len=0.3'
        lines.append('    node_{0}_image -> node_{0}_dummy [ {1} ];'.format(name, attrs))

        # end of subgraph
        lines.append('};')

        indent = ' ' * data['indent'] * 4
        for line in lines :
            self.fp.write("{0}{1}".format(indent, line))
            self.fp.write('\n')
        self.fp.write('\n')
