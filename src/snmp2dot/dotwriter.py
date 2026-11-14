import re

import logging
logger = logging.getLogger(__name__)

from jinja2 import Environment, FileSystemLoader

from .agent import Agent

from pprint import pprint

class DotWriter:

    def __init__(self, fp):
        self.fp = fp

        self.env = Environment(
            loader=FileSystemLoader("."),
            trim_blocks=True,
            lstrip_blocks=True,
        )

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

    def write_header(self, fp, data) :
        template = self.env.get_template('header.dot.j2')
        header = template.render(**data)
        fp.write(header)


    def write_footer(self, fp, data) :
        template = self.env.get_template('footer.dot.j2')
        footer = template.render(**data)
        fp.write(footer)

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


    def write_agent(self, data) :
        fp = self.fp

        indent = data['indent']
        minlen = data['minlen']

        image = data['image']
        
        if image is None :
            image = 'cisco/doc_png/small_hub.png'

        sysname = re.sub(r'\.', '_', data['sysname'])

        default_ifidx = data['default_ifidx']

        lines = []
        lines.append('// count is {0}'.format(Agent.count))
        Agent.count = Agent.count + 1

        lines.append('subgraph cluster_{0} {{'.format(sysname))
        #label = '{0}'.format(agent_ip)
        #label += '\n{0}'.format(agent_mac)
        #label += '\n{0}'.format(self.sysobjectid)

        label = data['sysname']

        lines.append('    label = "{0}";'.format(label))
        lines.append('')
        lines.append('    node_{0}_image ['.format(sysname))
        lines.append('        shape=none')
        lines.append('        image="{0}"'.format(image))
        lines.append('        label=""')
        lines.append('        fixedsize=true')
        lines.append('        imagescale=height')
        lines.append('    ];')
            
       
        lines.append('')

        line = '    // uplink port and downlink port'
        lines.append(line)

        for ifid in data['ifaces'] :
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
        
        for ifid in data['ifaces'] :
            if int(ifid) == int(data['default_ifidx']) :
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

        src = 'node_{0}_port{1}'.format(sysname, data['default_ifidx'])
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
        for ifid in data['ifaces'] :
            if int(ifid) == int(default_ifidx) :
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
        for port in data['dports']:
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

