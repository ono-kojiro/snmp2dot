import re

from .utils import *

__all__ = [
  'get_route_next_hop',
  'get_route_if_index',
]

def get_route_next_hop(data) :
    addr = None

    oidname = 'IP-FORWARD-MIB::ipCidrRouteNextHop'
    res = get_mib_data(data, oidname)
    if not res :
        return items

    for net_addr in res.keys():
        for mask in res[net_addr].keys():
            for i in res[net_addr][mask].keys():
                for value1 in res[net_addr][mask][i].keys():
                    addr = res[net_addr][mask][i][value1].get('val', None)
                    addr = re.sub(r'IpAddress: ', '', addr)
    return addr

def get_route_if_index(data) :
    ifidx = None

    oidname = 'IP-FORWARD-MIB::ipCidrRouteIfIndex'
    res = get_mib_data(data, oidname)
    if not res :
        return items

    for net_addr in res.keys():
        for mask in res[net_addr].keys():
            for i in res[net_addr][mask].keys():
                for value1 in res[net_addr][mask][i].keys():
                    ifidx = res[net_addr][mask][i][value1].get('val', None)
    return ifidx


