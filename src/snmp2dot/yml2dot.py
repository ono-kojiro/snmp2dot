#!/usr/bin/env python3

import sys
import os

import getopt
import json

import re
import yaml

import copy

from pprint import pprint

from .graph    import Graph
from .Edge     import Edge
from .terminal import Terminal
from .agent    import Agent
from .port     import Port
from .dotwriter import DotWriter

from .utils import *

import logging
logger = logging.getLogger(__name__)

def version():
    print('{0}'.format(snmp2dot.__version__))

def usage():
    print("Usage : {0}".format(sys.argv[0]))

def get_dports(agent_ip, uplink, conns) :
    dports = []
    
    logger.debug("in get_dports")

    for conn in conns :
        if conn['src_ip'] != agent_ip :
            continue
        port = conn['src_port']

        logger.debug("  port: {0}, uplink: {1}".format(port, uplink))

        if int(port) == int(uplink) :
            logger.debug("skip port {0}".format(port))
            continue

        # get all pnum from dports and create list
        port_list = [ dport.pnum for dport in dports ]
        if not port in port_list :
            dport = Port(None, agent_ip, port, Port.TYPE_AGENT)
            dports.append(dport)
    return dports

def main():
    ret = 0

    try:
        opts, args = getopt.gnu_getopt(
            sys.argv[1:],
            "hvo:c:l:d",
            [
                "help",
                "version",
                "output=",
                "config=",
                "logfile=",
                "debug",
            ]
        )
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)
    
    output = None
    configfile = None
    logfile = None
    debug = False

    configfiles = []

    for o, a in opts:
        if o in ("-v", "--version"):
            version()
            sys.exit(0)
        elif o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-c", "--config"):
            configfiles.append(a)
        elif o in ("-l", "--logfile"):
            logfile = a
        elif o in ("-d", "--debug"):
            debug = a
        elif o in ("-o", "--output"):
            output = a
        else:
            assert False, "unknown option"
	
    if output is not None :
        fp = open(output, mode='w', encoding='utf-8')
    else :
        fp = sys.stdout

    setup_logging(logfile, debug)

    if ret != 0:
        sys.exit(1)
    
    logger.debug('create Graph')
    graph = Graph()

    for filepath in args:
        data = read_yaml(filepath)

        items = data['agents']
        for item in items:
            sysname = item['sysname']
            ifaces  = item['interfaces']
            default_ifidx = item['default_ifidx']

            agent = Agent(
                        sysname=sysname,
                        ifaces=ifaces,
                        default_ifidx=default_ifidx,
                    )
            graph.add_agent(agent)

        items = data['terminals']
        for item in items:
            ip = item['ip']
            mac = item['mac']

            terminal = Terminal(ip=ip, mac=mac)
            graph.add_terminal(terminal)
        
        items = data['a2t_edges']
        for item in items:
            sysname = item['sysname']
            ifidx   = item['ifidx']
            mac = item['mac']
            ip = item['ip']
            default_ifidx = item['default_ifidx']

            src_name = re.sub(r'\.', '_', sysname)
            dst_name = re.sub(r'\:', '_', mac)

            src = 'node_{0}_port{1}'.format(src_name, ifidx)
            if default_ifidx != ifidx :
                dst = 'node_{0}_port1'.format(dst_name)
            else :
                dst = 'node_{0}_dummy'.format(dst_name)
                tmp = dst
                dst = src
                src = tmp

            edge = Edge(src=src, dst=dst)
            graph.add_edge(edge)

        items = data['a2a_edges']
        for item in items:
            sysname = item['sysname']
            ifidx   = item['ifidx']
            mac = item['mac']
            ip = item['ip']
            default_ifidx = item['default_ifidx']
            dst_sysname = item['dst_sysname']
            dst_ifidx = item['dst_ifidx']

            src_name = re.sub(r'\.', '_', sysname)
            
            dst_sysname = re.sub(r'\.', '_', dst_sysname)

            if src_name == dst_sysname :
                # maybe macvlan
                continue

            src = 'node_{0}_port{1}'.format(src_name, ifidx)
            dst = 'node_{0}_port{1}'.format(dst_sysname, dst_ifidx)
            
            if default_ifidx == ifidx :
                tmp = dst
                dst = src
                src = tmp

            edge = Edge(src=src, dst=dst)
            graph.add_edge(edge)

    writer = DotWriter(fp)
    writer.write_header(fp, graph.to_dict())

    for agent in graph.agents :
        writer.write_agent(agent.to_dict())

    for terminal in graph.terminals :
        writer.write_terminal(terminal.to_dict())

    for edge in graph.edges:
        writer.write_edge(edge.to_dict())

    writer.write_footer(fp, graph.to_dict())

    if output is not None :
        fp.close()
    sys.exit(0)

if __name__ == "__main__":
    main()
