#!/usr/bin/env python3

import sys
import os

import getopt
import json

import re
import yaml

import copy

from pprint import pprint

from snmp2dot.Graph    import Graph
from snmp2dot.Edge     import Edge
from snmp2dot.Terminal import Terminal
from snmp2dot.Agent    import Agent
from snmp2dot.Port     import Port

import logging

import snmp2dot

def version():
    print('{0}'.format(snmp2dot.__version__))

def usage():
    print("Usage : {0}".format(sys.argv[0]))

def read_json(filepath) :
    with open(filepath, mode='r', encoding='utf-8') as fp :
        data = json.loads(fp.read())
        return data

def read_yaml(filepath):
    fp = open(filepath, mode="r", encoding="utf-8")
    tmp = yaml.load(fp, Loader=yaml.loader.SafeLoader)
    data = copy.deepcopy(tmp)
    fp.close()

    return data

def get_dports(agent_ip, uplink, conns) :
    dports = []
    for conn in conns :
        if conn['src_ip'] != agent_ip :
            continue
        port = conn['src_port']
        if port == uplink :
            continue

        # get all pnum from dports and create list
        port_list = [ dport.pnum for dport in dports ]
        if not port in port_list :
            dport = Port(None, agent_ip, port, Port.TYPE_AGENT)
            dports.append(dport)
    return dports

def get_imagepath(configs, mac) :
    imagepath = None
    if mac in configs['images'] :
        imagepath = configs['images'][mac]
    return imagepath

def recursive_merge(dict1, dict2):
    for key, value in dict2.items():
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
            # If both values are dictionaries, recurse
            recursive_merge(dict1[key], value)
        else:
            # Otherwise, update (or add) the value
            dict1[key] = value
    return dict1

def main():
    ret = 0

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hvo:c:l:L:",
            [
                "help",
                "version",
                "output=",
                "config=",
                "logfile=",
                "loglevel=",
            ]
        )
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)
    
    output = None
    configfile = None
    logfile = None
    loglevel = 'info'

    for o, a in opts:
        if o in ("-v", "--version"):
            version()
            sys.exit(0)
        elif o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-c", "--config"):
            outputfile = a
        elif o in ("-l", "--logfile"):
            logfile = a
        elif o in ("-L", "--loglevel"):
            loglevel = a
        elif o in ("-o", "--output"):
            output = a
        else:
            assert False, "unknown option"
	
    if output is not None :
        fp = open(output, mode='w', encoding='utf-8')
    else :
        fp = sys.stdout

    if loglevel in ('info') :
        level = logging.INFO
    elif loglevel in ('warn', 'warning') :
        level = logging.WARNING
    elif loglevel in ('debug') :
        level = logging.DEBUG
    else :
        print('ERROR: unknown loglevel')
        ret += 1

    if logfile is not None:
        handler = logging.FileHandler(filename=logfile)
    else :
        handler = logging.StreamHandler(stream=sys.stderr)

    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S',
    )

    handler.setFormatter(formatter)
    logging.basicConfig(
        level = level,
        handlers = [
            handler
        ],
    )

    logger = logging.getLogger(sys.argv[0].split('/')[-1])

    if ret != 0:
        sys.exit(1)
	
    logger.info('create Graph')
    graph = Graph(logger=logger)

    configs = {}
    if configfile is None :
        if os.path.exists('./config.yml.local'):
            configfile = './config.yml.local'
            configs = recursive_merge(configs, read_yaml(configfile))
        pprint(configs)

        if os.path.exists('./config.yml'):
            configfile = './config.yml'
            configs = recursive_merge(configs, read_yaml(configfile))
        pprint(configs)

        if configfile is None :
            logger.error('ERROR: no config files')
            sys.exit(1)
    else :
        configs = read_yaml(configfile)

    pprint(configs)

    data = {}

    all_ports = []

    alt_ips = {}
    for ip in configs['nodes'] :
        if 'alternatives' in configs['nodes'][ip]:
            for alt_ip in configs['nodes'][ip]['alternatives']:
                alt_ips[alt_ip] = ip

    for jsonfile in args:
        data = read_json(jsonfile)
        agent_list = data['agents']
        a2a = data['agent2agent']
        a2t = data['agent2terminal']

        conns = a2a + a2t

        # agents
        for item in data['agents'] :
            agent_ip  = item['ip']
            agent_mac = item['mac']
            agent_descr = item['sysdescr']
            agent_objectid = item['sysobjectid']
            config = configs['nodes'][agent_ip]

            agent_uplink = config.get('uplink', None)
            
            uport = Port(agent_mac, agent_ip, agent_uplink, Port.TYPE_AGENT)
            dports = get_dports(agent_ip, agent_uplink, conns)
            imagepath = get_imagepath(configs, agent_mac)
            minlen = config.get('minlen', 4)

            agent = Agent(uport, dports, imagepath,
                          logger=logger,
                          minlen=minlen,
                          sysdescr=agent_descr,
                          sysobjectid=agent_objectid,
            )
            graph.add_agent(agent)

        all_ports.extend(graph.get_agent_uports())
        all_ports.extend(graph.get_agent_dports())
        
        # edges
        for conn in conns :
            src_ip   = conn['src_ip']
            src_port = conn['src_port']
            dst_mac   = conn['dst_mac']
            dst_ip    = conn['dst_ip']

            dst_port = "1"

            if dst_ip is None :
                for agent in graph.agents :
                    if agent.uport.mac == dst_mac :
                        dst_ip = agent.uport.ip

            if dst_ip in alt_ips :
                dst_ip = alt_ips[dst_ip]

            target = None
            for port in all_ports :
                if port.ip == src_ip and port.pnum == src_port :
                    target = port
                    break

            if target is None :
                print('WARN: no port found, {0}, {1}'.format(src_ip, src_port))
                sys.exit(1)

            # add
            #sport = Port(None, src_ip, src_port)
            sport = target

            sport.set_uplink(False)
            dport = Port(dst_mac, dst_ip, dst_port)


            is_src_port_uplink = False
            is_available = True

            if src_ip in configs['nodes'] : 
                config = configs['nodes'][src_ip]
                uplink = config.get('uplink', None)

                if src_port == uplink :
                    is_src_port_uplink = True
                    # add
                    sport.set_uplink(True)

                draw_uplink_edge = config.get('draw_uplink_edge', None)
                if is_src_port_uplink and draw_uplink_edge != True:
                    is_available = False
            
            # if dst is Agent, use uplink port number
            if dst_ip in configs['nodes']:
                uplink = configs['nodes'][dst_ip].get('uplink', None)
                dst_port = uplink

                # add
                dport.set_pnum(uplink)
                
            #edge = Edge(src_ip, src_port, dst_mac, dst_ip, dst_port, \
            #            is_src_port_uplink, is_available)
            edge = Edge(sport, dport, is_available)
            graph.add_edge(edge)
        
        # terminals
        for conn in a2t:
            mac = conn['dst_mac']
            ip  = conn['dst_ip']
            dst_port = "1"

            imagepath = None
            if mac in configs['images'] :
                imagepath = configs['images'][mac]
            
            dport = Port(mac, ip, dst_port, Port.TYPE_TERMINAL)

            edge = graph.get_edge_by_dst_mac(mac)

            terminal = Terminal(dport, imagepath, \
                    edge.sport.is_uplink)

            graph.add_terminal(terminal)

        # swap edge
        for edge in graph.edges :
            if edge.sport.is_uplink :
                tmp = edge.sport
                edge.sport = edge.dport
                edge.dport = tmp

                for terminal in graph.terminals :
                    if terminal.dport.mac == edge.sport.mac :
                        terminal.port_order = 1

        for edge in graph.edges :
            ip = edge.sport.ip
            if ip in alt_ips:
                ip = alt_ips[ip]
                edge.sport.ip = ip
                if ip in configs['nodes']:
                    if 'uplink' in configs['nodes'][ip] :
                        uplink = configs['nodes'][ip].get('uplink', None)
                        edge.sport.pnum = uplink

            ip = edge.dport.ip
            if ip in alt_ips:
                ip = alt_ips[ip]
                edge.dport.ip = ip
                if ip in configs['nodes']:
                    if 'uplink' in configs['nodes'][ip] :
                        uplink = configs['nodes'][ip].get('uplink', None)
                        edge.dport.pnum = uplink

        graph.update_edges()
    
    graph.print(fp)

    if output is not None :
        fp.close()

if __name__ == "__main__":
    main()
