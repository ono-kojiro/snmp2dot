import sys
import re

from .port import Port

from pprint import pprint, pformat

import logging
logger = logging.getLogger(__name__)

class Graph() :
    def __init__(self) :
        self.rankdir = "LR"
        self.ordering = "out"
        self.nodesep = "0.1"
        self.ranksep = "0.3"
        self.splines = "false"
        self.overlap = "false"

        self.subgraphs = []

        self.agents = []
        self.terminals = []
        self.edges = []

        self.imagepath = '/usr/share/icons'

    def to_dict(self):
        data = {
            'imagepath': self.imagepath,
            'rankdir': self.rankdir,
            'ordering': self.ordering,
            'nodesep': self.nodesep,
            'ranksep': self.ranksep,
            'splines': self.splines,
            'overlap': self.overlap,
            'subgraphs': self.subgraphs,
            'agents': self.agents,
            'terminals': self.terminals,
            'edges': self.edges,
        }

        return data

    def add_subgraph(self, subgraph) :
        self.subgraphs.append(subgraph)
    
    def add_agent(self, agent) :
        self.agents.append(agent)
    
    def add_terminal(self, terminal) :
        self.terminals.append(terminal)

    def add_edge(self, edge) :
        self.edges.append(edge)

    def get_agent_uports(self) :
        items = []
        for agent in self.agents :
            items.append(agent.uport)
        return items

    def get_agent_dports(self) :
        items = []
        for agent in self.agents :
            items.extend(agent.dports)
        return items

    def get_edge_by_dst_mac(self, mac) :
        item = None
        for edge in self.edges :
            if edge.dport.mac == mac :
                item = edge
                break
        return item

    def update_edges(self) :
        dst2src = {}
        src2dst = {}
                
        logger.debug('check edges')

        for edge in self.edges :
            if not edge.is_available :
                continue

            dst = str(edge.dport)
            if not dst in dst2src :
                dst2src[dst] = []
            dst2src[dst].append(edge.sport)

            src = str(edge.sport)
            if not src in src2dst :
                src2dst[src] = []
            src2dst[src].append(edge.dport)

        targets = {}
        for dst in dst2src :
            num_src = len(dst2src[dst])
            if num_src == 1:
                continue
            logger.debug('len of dst2src is {0}'.format(num_src))

            for sport in dst2src[dst]:
                src = str(sport)
                num_dst = len(src2dst[src])
                if num_dst > 1 or sport.is_uplink :
                    if not src in targets :
                        targets[src] = {}
                    if not dst in targets[src] :
                        targets[src][dst] = 1

        for edge in self.edges :
            if not edge.is_available:
                continue
            dst = str(edge.dport)
            src = str(edge.sport)
            if src in targets and dst in targets[src] :
                logger.debug('disable src:{0} to dst:{1}'.format(src, dst))
                edge.is_available = False
