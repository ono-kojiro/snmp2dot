#!/usr/bin/env python3

import sys

import getopt
import json
import yaml
import copy

import re

import sqlite3
from pprint import pprint


import snmp2dot

import logging
logger = logging.getLogger(__name__)

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

def get_scalar_value(data, oidname) :
    val = None

    mibname, objname = re.split(r'::', oidname)

    res = data.get(mibname, None)
    if res is None:
        return val

    res = res.get(objname, None)
    if res is None:
        return val

    return res['val']

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
        pprint(ifid, stream=sys.stderr)
        for addr in res[ifid]:
            item = res[ifid][addr]
            pprint(item)
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

def normalize_mac(mac_str) :
    if mac_str is None :
        return None

    mac_str = re.sub(r'\s+$', '', mac_str)
    expr = r"([0-9a-fA-F ]{1,2})" + r"([-: ]?([0-9a-fA-F]{1,2}))" * 5 + r"$"
    m = re.match(expr, mac_str.lower())
    mac = ''

    if m :
        # 1, 3, 5, ... , 11
        for i in range(1, 12, 2) :
            val = int(m.group(i), 16)
            mac += ":{0:02x}".format(val)
        mac = re.sub(r'^:', '', mac)
        #print("DEBUG: {0} -> {1}".format(mac_str, mac))
    else :
        print("ERROR: invalid mac address, '{0}'".format(mac_str))
        sys.exit(1)

    return mac

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
    sql += 'sysobjectid TEXT '
    sql += ');'

    c.execute(sql)

def create_interfaces_table(conn, table):
    c = conn.cursor()

    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'sysname TEXT, '
    sql += 'idx INTEGER, '
    sql += 'typ TEXT, '
    sql += 'status TEXT, '
    sql += 'descr TEXT, '
    sql += 'phys TEXT '
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
    sql += 'ORDER BY ifidx ASC '
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
    sql += 'SELECT '
    sql += '  interfaces_table.sysname AS sysname, '
    sql += '  interfaces_table.idx AS idx, '
    sql += '  macaddrs_table.mac AS mac '
    sql += 'FROM interfaces_table '
    sql += 'LEFT OUTER JOIN macaddrs_table '
    sql += '  ON interfaces_table.idx = macaddrs_table.idx '
    sql += 'WHERE status = "up(1)" '
    sql += ';'

    c.execute(sql)


def insert_interface(conn, table, item):
    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ?, ?, ?, ? );'.format(table)
    lst = [
        item['sysname'],
        item['idx'],
        item['typ'],
        item['status'],
        item['descr'],
        item['phys'],
    ]

    c.execute(sql, lst)

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
    pprint(item)
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ?);'.format(table)
    lst = [
        item['sysname'],
        item['idx'],
        item['mac'],
    ]

    c.execute(sql, lst)

def insert_agent(conn, table, item):
    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ?, ?, ?);'.format(table)
    lst = [
        item['sysname'],
        item['ip'],
        item['mac'],
        item['sysdescr'],
        item['sysobjectid'],
    ]
    c.execute(sql, lst)

def create_agents_view(conn, view):
    c = conn.cursor()

    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT '
    sql += '  DISTINCT sysname, ip, mac, sysdescr, sysobjectid '
    sql += 'FROM agents_table '
    sql += ';'

    c.execute(sql)

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
    create_interfaces_table(conn, 'interfaces_table')
    create_macaddrs_table(conn, 'macaddrs_table')

    create_ifindexes_table(conn, 'ifindexes_table')

    create_netaddrs_table(conn, 'netaddrs_table')
    create_physaddrs_table(conn, 'physaddrs_table')
    
    create_netaddrs_view(conn, 'netaddrs_view')
    create_physaddrs_view(conn, 'physaddrs_view')

    # for buffalo
    create_fdbports_table(conn, 'fdbports_table')
    create_fdbaddrs_table(conn, 'fdbaddrs_table')
    create_fdbaddrs_view(conn, 'fdbaddrs_view')

    create_connections_view(conn, 'connections_view')

    for jsonfile in args:
        data = read_json(jsonfile)

        sysname  = get_scalar_value(data, 'SNMPv2-MIB::sysName.0')
        sysdescr = get_scalar_value(data, 'SNMPv2-MIB::sysDescr.0')
        sysobjectid = get_scalar_value(data, 'SNMPv2-MIB::sysObjectID.0')
        print('DEBUG: sysobjectid is {0}'.format(sysobjectid))

        ips = get_agent_address(data)
        logging.debug('found {0}'.format(ips))

        mac = get_scalar_value(data, 'BRIDGE-MIB::dot1dBaseBridgeAddress.0')
        mac = normalize_mac(mac)
       
        for ip in ips:
            item = {
                'sysname': sysname,
                'sysdescr': sysdescr,
                'sysobjectid': sysobjectid,
                'ip': ip,
                'mac': mac,
            }

            insert_agent(conn, 'agents_table', item)

        if2status = get_dict_values(data, 'IF-MIB::ifOperStatus')
        if2descr  = get_dict_values(data, 'IF-MIB::ifDescr')
        if2type   = get_dict_values(data, 'IF-MIB::ifType')
        ifaces = get_dict_values(data, 'IF-MIB::ifIndex')
        
        if2phys = get_dict_values(data, 'IF-MIB::ifPhysAddress')

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

        for iface in ifaces :
            status = if2status[iface]
            descr  = if2descr[iface]
            typ    = if2type[iface]
            phys = if2phys[iface]
       
            if phys != '' :
                phys = normalize_mac(phys)

            item = {
                'sysname': sysname,
                'idx': iface,
                'typ' : typ,
                'status': status,
                'descr': descr,
                'phys' : phys,
            }
            insert_interface(conn, 'interfaces_table', item)
        
        if2macs = get_if2mac_table(data, 'BRIDGE-MIB::dot1dTpFdbPort')
        for iface in ifaces :
            if not iface in if2macs:
                continue

            macs = if2macs[iface]
            for mac in macs:
                item = {
                    'sysname': sysname,
                    'idx'  : iface,
                    'mac'  : mac,
                }
                insert_macaddr(conn, 'macaddrs_table', item)

        # for OPNsense
        # ex. agent_macs[ifid] = [ mac1, mac2, ...]
        agent_macs = get_ifPhysAddress(data)

        # for OPNsense
        if2macs = get_ipNetToMediaPhysAddress(data)
        pprint(if2macs)
        for iface in ifaces :
            if not iface in if2macs:
                continue

            macs = if2macs[iface]
            for mac in macs:
                if iface in agent_macs:
                    if mac in agent_macs[iface]:
                        continue

                item = {
                    'sysname' : sysname,
                    'idx'  : iface,
                    'mac'  : mac,
                }
                insert_macaddr(conn, 'macaddrs_table', item)

    create_agents_view(conn, 'agents_view')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
