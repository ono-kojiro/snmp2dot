#!/usr/bin/env python3

import sys

import getopt
import json
import yaml
import copy

import re

import sqlite3
from pprint import pprint

import logging
logger = logging.getLogger(__name__)

from .sysname import *
from .interfaces import *
from .utils import *
from .agent2agent import *
from .agent2terminal import *

from .views import *

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

def get_mib_data(data, oidname) :
    # ex. oidname = 'RFC1213-MIB::atNetAddress'
    mibname, objname = re.split(r'::', oidname)
    
    res = data.get(mibname, None)
    if res is None:
        return res

    res = res.get(objname, None)
    return res

def get_mac2addrs_table(data) :
    mac2addrs = {}

    #ip_mib = data.get('IP-MIB', None)
    ip_mib = data.get('RFC1213-MIB', None)
    if ip_mib :
       addrs = ip_mib.get('ipNetToMediaPhysAddress', None)
       if addrs :
           for tmp in addrs:
              items = addrs[tmp]
              for addr in items:
                  mac = items[addr]['val']
                  mac = normalize_mac(mac)

                  if not mac in mac2addrs :
                    mac2addrs[mac] = []
                  mac2addrs[mac].append(addr)

    return mac2addrs

def get_dict_values(data, oidname) :
    records = {}

    mibname, objname = re.split(r'::', oidname)

    res = data.get(mibname, None)
    if res is None:
        return records

    res = res.get(objname, None)
    if res is None:
        return records

    for key in res:
        item = res[key]
        val = item['val']
        records[key] = val

    return records

def get_agent_address(data) :
    addrs = []

    oidname = 'RFC1213-MIB::ipAdEntAddr'
    val = None
    mibname, objname = re.split(r'::', oidname)

    res = data.get(mibname, None)
    if res is None:
        return addrs

    res = res.get(objname, None)
    if res is None:
        return addrs

    for attr in res:
        item = res[attr]
        val = item['val']
        if re.search(r'169\.254\.', val) :
            continue
        if re.search(r'127\.0\.0\.1', val) :
            continue
        addrs.append(val)

    return addrs

def hex2addr(hex_str) :
    addr = ''
    items = re.split(r':', hex_str)
    for item in items:
        val = int(item, 16)
        addr += '.{0}'.format(val)

    addr = re.sub(r'^\.', '', addr)
    return addr

def get_at_if_index(data) :
    items = []

    oidname = 'RFC1213-MIB::atIfIndex'
    res = get_mib_data(data, oidname)
    if not res :
        return items

    for ifidx in res:
        # ex. ifidx="23"
        
        for idx in res[ifidx] :
            # ex. idx: '1.192.168.122.10'

            val = res[ifidx][idx]['val']

            item = {
                'idx' : idx,
                'ifidx' : int(val),
            }
            items.append(item)

    return items

def get_at_net_address(data) :
    items = []

    oidname = 'RFC1213-MIB::atNetAddress'
    res = get_mib_data(data, oidname)
    if not res :
        return items

    for ifidx in res:
        # ex. ifidx="23"
        
        for idx in res[ifidx] :
            # ex. idx: '1.192.168.122.10'

            val = res[ifidx][idx]['val']
            netaddr = hex2addr(val)

            item = {
                'ifidx' : int(ifidx),
                'idx' : idx,
                'netaddr' : netaddr,
            }
            items.append(item)

    return items

def get_at_phys_address(data) :
    items = []

    oidname = 'RFC1213-MIB::atPhysAddress'
    res = get_mib_data(data, oidname)
    if not res :
        return items

    for ifidx in res:
        # ex. idx="23"
        
        for idx in res[ifidx] :
            # ex. idx: '1.192.168.122.10'

            physaddr = res[ifidx][idx]['val']
            physaddr = normalize_mac(physaddr)

            item = {
                'ifidx' : int(ifidx),
                'idx' : idx,
                'physaddr' : physaddr,
            }
            items.append(item)

    return items

def get_default_ifidx(data):
    
    items = []
    oidname = 'RFC1213-MIB::ipRouteIfIndex'

    res = get_mib_data(data, oidname)
    if not res :
        return items

    for addr in res:
        # ex. idx="0.0.0.0"
        val = res[addr]['val']

        item = {
            'addr' : addr,
            'ifidx' : val,
        }
        items.append(item)

    default_ifidx = None
    for item in items:
        if '0.0.0.0' in item['addr'] :
            default_ifidx = item['ifidx']
            break

    return default_ifidx

def get_default_router_ip(data):
    items = []

    oidname = 'RFC1213-MIB::ipRouteNextHop'
    res = get_mib_data(data, oidname)
    if not res :
        return items

    default_router_ip = None

    for addr in res.keys():
        if addr == '0.0.0.0' :
            default_router_ip = res[addr]['val']
        
    return default_router_ip

# for buffalo
def get_mac2addr(data) :
    items = []

    oidname = 'BRIDGE-MIB::dot1dTpFdbAddress'
    res = get_mib_data(data, oidname)
    if not res :
        return items

    for idx_mac in res:
        # ex. idx_mac="STRING: xx:xx:xx:xx:xx:xx"
        addr = res[idx_mac]['val']
        addr = normalize_mac(addr)

        item = {
            'idx' : idx_mac,
            'physaddr' : addr,
        }
        items.append(item)

    return items

# for buffalo
def get_mac2port(data) :
    items = []

    oidname = 'BRIDGE-MIB::dot1dTpFdbPort'
    res = get_mib_data(data, oidname)
    if not res :
        return items

    for idx_mac in res:
        # ex. idx_mac="STRING: xx:xx:xx:xx:xx:xx"
        port = res[idx_mac]['val']

        item = {
            'idx' : idx_mac,
            'ifidx' : int(port),
        }
        items.append(item)

    return items

def get_ifPhysAddress(data):
    records = {}

    oidname = "IF-MIB::ifPhysAddress"
    mibname, objname = re.split(r'::', oidname)
    
    res = data.get(mibname, None)
    if res is None:
        return records

    res = res.get(objname, None)
    if res is None:
        return records
    
    for ifid in res:
        item = res[ifid]
        typ = item['typ']
        mac = item['val']
        if mac == '' :
            continue
        mac = normalize_mac(mac)

        if not ifid in records:
            records[ifid] = []

        records[ifid].append(mac)
    return records

def get_ifid_ip_mac_list(data):
    items = {}

    oidname = "RFC1213-MIB::ipNetToMediaPhysAddress"
    res = get_mib_data(data, oidname)
    if not res :
        return items

    for ifidx in res.keys():
        if not ifidx in items :
            items[ifidx] = {}

        for ip in res[ifidx].keys() :
            mac = res[ifidx][ip]['val']
            mac = normalize_mac(mac)

            items[ifidx][ip] = mac

    return items

def get_ipNetToMediaPhysAddress(data):
    records = {}

    oidname = "RFC1213-MIB::ipNetToMediaPhysAddress"
    mibname, objname = re.split(r'::', oidname)

    res = data.get(mibname, None)
    if res is None:
        return records

    res = res.get(objname, None)
    if res is None:
        return records

    for ifid in res:
        for addr in res[ifid]:
            item = res[ifid][addr]
            typ = item['typ']
            mac = item['val']
            mac = normalize_mac(mac)

            if not ifid in records:
                records[ifid] = []

            records[ifid].append(mac)
    return records

def get_if2mac_table(data, oidname) :
    records = {}

    mibname, objname = re.split(r'::', oidname)

    res = data.get(mibname, None)
    if res is None:
        return records

    res = res.get(objname, None)
    if res is None:
        return records

    for mac in res:
        item = res[mac]
        iface = item['val']
        mac = re.sub(r'^STRING: ', '', mac)
        mac = normalize_mac(mac)
        if not iface in records:
            records[iface] = []

        records[iface].append(mac)

    return records

def get_mac2status_table(data, oidname) :
    records = {}

    mibname, objname = re.split(r'::', oidname)

    res = data.get(mibname, None)
    if res is None:
        return records

    res = res.get(objname, None)
    if res is None:
        return records

    for mac in res:
        item = res[mac]
        status = item['val']
        mac = re.sub(r'^STRING: ', '', mac)
        mac = normalize_mac(mac)
        records[mac] = status

    return records

def create_agents_table(conn, table):
    c = conn.cursor()

    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'sysname TEXT, '
    sql += 'ip TEXT, '
    sql += 'mac TEXT, '
    sql += 'sysdescr TEXT, '
    sql += 'sysobjectid TEXT, '
    sql += 'default_ifidx TEXT '
    sql += ');'

    c.execute(sql)

def create_ifindexes_table(conn, table):
    c = conn.cursor()

    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'sysname TEXT, '
    sql += 'ifidx INTEGER, '
    sql += 'idx TEXT '
    sql += ');'

    c.execute(sql)

def create_netaddrs_table(conn, table):
    c = conn.cursor()

    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'sysname TEXT, '
    sql += 'ifidx INTEGER, '
    sql += 'idx TEXT, '
    sql += 'netaddr TEXT '
    sql += ');'

    c.execute(sql)

def create_physaddrs_table(conn, table):
    c = conn.cursor()

    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'sysname TEXT, '
    sql += 'ifidx INTEGER, '
    sql += 'idx TEXT, '
    sql += 'physaddr TEXT '
    sql += ');'

    c.execute(sql)

def create_netaddrs_view(conn, view):
    c = conn.cursor()

    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT '
    sql += '  netaddrs_table.sysname AS sysname, '
    sql += '  netaddrs_table.ifidx   AS ifidx, '
    sql += '  netaddrs_table.netaddr AS netaddr, '
    sql += '  physaddrs_table.physaddr AS physaddr '
    sql += 'FROM netaddrs_table '
    sql += 'LEFT OUTER JOIN physaddrs_table ON ('
    sql += '  netaddrs_table.sysname = physaddrs_table.sysname AND '
    sql += '  netaddrs_table.ifidx = physaddrs_table.ifidx AND '
    sql += '  netaddrs_table.idx = physaddrs_table.idx '
    sql += '  ) '
    sql += 'ORDER BY sysname ASC, ifidx ASC, netaddr ASC '
    sql += ';'

    c.execute(sql)

def create_physaddrs_view(conn, view):
    c = conn.cursor()

    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT '
    sql += '  physaddrs_table.sysname  AS sysname, '
    sql += '  physaddrs_table.ifidx    AS ifidx, '
    sql += '  physaddrs_table.physaddr AS physaddr '
    sql += 'FROM physaddrs_table '
    sql += ';'

    c.execute(sql)

def create_connections_view(conn, view) :
    c = conn.cursor()

    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql =  'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT * FROM physaddrs_view '
    sql += '  UNION ALL '
    sql += 'SELECT * FROM fdbaddrs_view '
    sql += ';'

    c.execute(sql)



def create_macaddrs_table(conn, table):
    c = conn.cursor()

    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'sysname TEXT, '
    sql += 'idx INTEGER, '
    sql += 'mac TEXT '
    sql += ');'

    c.execute(sql)

# for buffalo
def create_fdbports_table(conn, table):
    c = conn.cursor()

    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'sysname TEXT, '
    sql += 'ifidx INTEGER, '
    sql += 'idx TEXT '
    sql += ');'

    c.execute(sql)

# for buffalo
def insert_fdbport(conn, table, sysname, item):
    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ? );'.format(table)
    lst = [
        sysname,
        item['ifidx'],
        item['idx'],
    ]

    c.execute(sql, lst)

# for buffalo
def create_fdbaddrs_table(conn, table):
    c = conn.cursor()

    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'sysname TEXT, '
    sql += 'idx TEXT, '
    sql += 'physaddr TEXT '
    sql += ');'

    c.execute(sql)

# for buffalo
def create_fdbaddrs_view(conn, view):
    c = conn.cursor()

    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT '
    sql += '  fdbaddrs_table.sysname  AS sysname, '
    sql += '  fdbports_table.ifidx    AS ifidx, '
    sql += '  fdbaddrs_table.physaddr AS physaddr '
    sql += 'FROM fdbaddrs_table '
    sql += 'LEFT OUTER JOIN fdbports_table ON ('
    sql += '  fdbaddrs_table.sysname = fdbports_table.sysname AND '
    sql += '  fdbaddrs_table.idx = fdbports_table.idx '
    sql += ') '
    sql += 'WHERE fdbports_table.ifidx != 0 '
    sql += 'ORDER BY ifidx ASC '
    sql += ';'

    c.execute(sql)


# for buffalo
def insert_fdbaddr(conn, table, sysname, item):
    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ? );'.format(table)
    lst = [
        sysname,
        item['idx'],
        item['physaddr'],
    ]

    c.execute(sql, lst)

def create_macaddrs_view(conn, view):
    c = conn.cursor()

    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT DISTINCT '
    sql += '  interfaces_table.sysname AS sysname, '
    sql += '  interfaces_table.idx AS idx, '
    sql += '  macaddrs_table.mac AS mac '
    sql += 'FROM interfaces_table '
    sql += 'LEFT OUTER JOIN macaddrs_table '
    sql += '  ON interfaces_table.idx = macaddrs_table.idx '
    sql += 'WHERE status = "up(1)" '
    sql += ';'

    c.execute(sql)

def create_graph_view(conn, view):
    c = conn.cursor()
    
    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)
    
    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT DISTINCT '
    sql += '  conns_view.sysname AS sysname, '
    sql += '  conns_view.ifidx   AS ifidx, '
    sql += '  conns_view.physaddr AS mac, '
    sql += '  arp_table.ip  AS ip '
    sql += 'FROM conns_view '
    sql += 'LEFT OUTER JOIN arp_table ON ('
    sql += '  conns_view.physaddr = arp_table.mac '
    sql += ') '
    sql += 'ORDER BY sysname ASC, ifidx ASC, mac ASC, ip ASC '
    sql += ';'
    
    c.execute(sql)


def insert_ifindex(conn, table, sysname, item):
    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ?);'.format(table)
    lst = [
        sysname,
        item['ifidx'],
        item['idx'],
    ]

    c.execute(sql, lst)

def insert_netaddr(conn, table, sysname, item):
    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ?, ?);'.format(table)
    lst = [
        sysname,
        item['ifidx'],
        item['idx'],
        item['netaddr'],
    ]

    c.execute(sql, lst)

def insert_physaddr(conn, table, sysname, item):
    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ?, ?);'.format(table)
    lst = [
        sysname,
        item['ifidx'],
        item['idx'],
        item['physaddr'],
    ]

    c.execute(sql, lst)

def insert_macaddr(conn, table, item):
    c = conn.cursor()
    #pprint(item)

    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ?);'.format(table)
    lst = [
        item['sysname'],
        item['idx'],
        item['mac'],
    ]

    c.execute(sql, lst)

def insert_agent(conn, table, item):
    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ?, ?, ?, ? );'.format(table)
    lst = [
        item['sysname'],
        item['ip'],
        item['mac'],
        item['sysdescr'],
        item['sysobjectid'],
        item['default_ifidx'],
    ]
    c.execute(sql, lst)

def create_agents_view(conn, view):
    c = conn.cursor()

    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT '
    sql += '  DISTINCT sysname, mac, sysdescr, sysobjectid, default_ifidx '
    sql += 'FROM agents_table '
    sql += ';'

    c.execute(sql)

def detect_default_router_port(data, invalid_default_ifidx):
    default_router_ip = get_default_router_ip(data)
    
    ifid_ip_mac_list = get_ifid_ip_mac_list(data)
    ip_mac_list = ifid_ip_mac_list[invalid_default_ifidx]
    default_router_mac = ip_mac_list[default_router_ip]
    
    mac2port = get_mac2port(data)

    default_router_port = None
    for item in mac2port :
        idx_mac = item['idx']
        ifidx   = item['ifidx']
        mac = re.sub(r'STRING: ', '', idx_mac)
        mac = normalize_mac(mac)
        if default_router_mac == mac :
            default_router_port = ifidx
            break

    return default_router_port
        
def main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hvo:",
            [
                "help",
                "version",
                "output=",
            ]
        )
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)
    
    output = None
	
    for o, a in opts:
        if o in ("-v", "--version"):
            version()
            sys.exit(0)
        elif o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-o", "--output"):
            output = a
        else:
            assert False, "unknown option"
	
    ret = 0

    if output is None :
        print("no output option", file=sys.stderr)
        ret += 1
	
    if ret != 0:
        sys.exit(1)

    logging.basicConfig(level=logging.DEBUG)

    conn = sqlite3.connect(output)
    create_agents_table(conn, 'agents_table')
    create_interfaces_table(conn)
    create_interfaces_view(conn)
    create_macaddrs_table(conn, 'macaddrs_table')

    create_ifindexes_table(conn, 'ifindexes_table')

    create_netaddrs_table(conn, 'netaddrs_table')
    create_physaddrs_table(conn, 'physaddrs_table')
    
    create_netaddrs_view(conn, 'netaddrs_view')
    create_physaddrs_view(conn, 'physaddrs_view')
    create_macaddrs_view(conn, 'macaddrs_view')
    
    # for buffalo
    create_fdbports_table(conn, 'fdbports_table')
    create_fdbaddrs_table(conn, 'fdbaddrs_table')
    create_fdbaddrs_view(conn, 'fdbaddrs_view')

    create_connections_view(conn, 'conns_view')

    # for graph
    create_graph_view(conn, 'graph_view')

    create_sysnames_table(conn)
    
    create_agent2agent_view(conn)
    create_agent2terminal_view(conn)

    create_a2t_edges_view(conn)
    create_a2a_edges_view(conn)

    for jsonfile in args:
        data = read_json(jsonfile)

        sysname  = get_scalar_value(data, 'SNMPv2-MIB::sysName.0')
        sysdescr = get_scalar_value(data, 'SNMPv2-MIB::sysDescr.0')
        sysobjectid = get_scalar_value(data, 'SNMPv2-MIB::sysObjectID.0')
        ifnumber = get_scalar_value(data, 'IF-MIB::ifNumber.0')

        #print('DEBUG: sysobjectid is {0}'.format(sysobjectid))

        ips = get_agent_address(data)
        logging.debug('found {0}'.format(ips))

        mac = get_scalar_value(data, 'BRIDGE-MIB::dot1dBaseBridgeAddress.0')
        mac = normalize_mac(mac)
        
        # for OPNsense
        if2macs = get_ipNetToMediaPhysAddress(data)
        
        default_ifidx = get_default_ifidx(data)

        if int(default_ifidx) > int(ifnumber) :
            print('WARNING: invalid default_ifidx')
            default_ifidx = detect_default_router_port(data, default_ifidx)
            print('WARNING: changed default_ifidx to {0}'.format(default_ifidx))
        
        item = {
            'sysname': sysname,
            'sysdescr': sysdescr,
            'sysobjectid': sysobjectid,
            'ip' : '',
            'mac': mac,
            'default_ifidx' : default_ifidx,
        }
        insert_agent(conn, 'agents_table', item)

        insert_sysname(conn, sysname)

        # extract RFC1213-MIB::atIfIndex
        items = get_at_if_index(data)
        for item in items :
            insert_ifindex(conn, 'ifindexes_table', sysname, item)

        # extract RFC1213-MIB::atNetAddress
        items = get_at_net_address(data)
        for item in items :
            insert_netaddr(conn, 'netaddrs_table', sysname, item)
        
        # extract RFC1213-MIB::atPhysAddress
        items = get_at_phys_address(data)
        for item in items :
            insert_physaddr(conn, 'physaddrs_table', sysname, item)

        # for buffalo
        items = get_mac2port(data)
        for item in items :
            insert_fdbport(conn, 'fdbports_table', sysname, item)
        
        items = get_mac2addr(data)
        for item in items :
            insert_fdbaddr(conn, 'fdbaddrs_table', sysname, item)

        #
        # create interfaces_table
        #
        build_interfaces_table(conn, data)

    create_agents_view(conn, 'agents_view')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
