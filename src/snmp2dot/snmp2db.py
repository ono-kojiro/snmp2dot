#!/usr/bin/env python3

import sys

import getopt
import json

import re

import sqlite3
from pprint import pprint

import snmp2dot

def version():
    print('{0}'.format(snmp2dot.__version__))

def usage():
    print("Usage : {0}".format(sys.argv[0]))

def read_json(filepath) :
    with open(filepath, mode='r', encoding='utf-8') as fp :
        data = json.loads(fp.read())
        return data

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

def get_ip_address(data) :
    addrs = []

    #oidname = 'IP-MIB::ipAdEntAddr'
    oidname = 'RFC1213-MIB::ipAdEntAddr'
    val = None
    mibname, objname = re.split(r'::', oidname)

    res = data.get(mibname, None)
    if res is None:
        return val

    res = res.get(objname, None)
    if res is None:
        return val

    for attr in res:
        item = res[attr]
        val = item['val']
        if re.search(r'169\.254\.', val) :
            continue
        if re.search(r'127\.0\.0\.1', val) :
            continue
        addrs.append(val)

    return addrs

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
        print("ERROR: invalid mac address, {0}".format(mac_str))
        sys.exit(1)

    return mac

def create_agents_table(conn, table):
    c = conn.cursor()

    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'ip TEXT, '
    sql += 'mac TEXT, '
    sql += 'sysdescr TEXT '
    sql += ');'

    c.execute(sql)

def create_interfaces_table(conn, table):
    c = conn.cursor()

    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'agent TEXT, '
    sql += 'idx TEXT, '
    sql += 'typ TEXT, '
    sql += 'status TEXT, '
    sql += 'descr TEXT '
    sql += ');'

    c.execute(sql)

def create_macaddrs_table(conn, table):
    c = conn.cursor()

    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'agent TEXT, '
    sql += 'idx TEXT, '
    sql += 'mac TEXT '
    sql += ');'

    c.execute(sql)

def create_macaddrs_view(conn, view):
    c = conn.cursor()

    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT '
    sql += '  interfaces_table.agent AS agent, '
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
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ?, ?, ?);'.format(table)
    lst = [
        item['agent'],
        item['idx'],
        item['typ'],
        item['status'],
        item['descr'],
    ]

    c.execute(sql, lst)

def insert_macaddr(conn, table, item):
    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ?);'.format(table)
    lst = [
        item['agent'],
        item['idx'],
        item['mac'],
    ]

    c.execute(sql, lst)


def insert_agent(conn, table, item):
    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ?);'.format(table)
    lst = [
        item['ip'],
        item['mac'],
        item['sysdescr'],
    ]
    c.execute(sql, lst)

def main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hvo:",
            [
                "help",
                "version",
                "output="
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

    conn = sqlite3.connect(output)
    create_agents_table(conn, 'agents_table')
    create_interfaces_table(conn, 'interfaces_table')
    create_macaddrs_table(conn, 'macaddrs_table')

    for jsonfile in args:
        data = read_json(jsonfile)

        sysdescr = get_scalar_value(data, 'SNMPv2-MIB::sysDescr.0')
        ips = get_ip_address(data)
        mac = get_scalar_value(data, 'BRIDGE-MIB::dot1dBaseBridgeAddress.0')
        mac = normalize_mac(mac)

        if len(ips) != 1 :
            print('WARNING: some IP address found', file=sys.stderr)
            print('WARNING: ips {0}'.format(ips))
            print('WARNING: use only {0}'.format(ips[0]))
            #sys.exit(1)
            
        ip = ips[0]

        item = {
            'sysdescr': sysdescr,
            'ip': ip,
            'mac': mac,
        }
        insert_agent(conn, 'agents_table', item)

        if2status = get_dict_values(data, 'IF-MIB::ifOperStatus')
        if2descr  = get_dict_values(data, 'IF-MIB::ifDescr')
        if2type   = get_dict_values(data, 'IF-MIB::ifType')
        ifaces = get_dict_values(data, 'IF-MIB::ifIndex')
        
        for iface in ifaces :
            status = if2status[iface]
            descr  = if2descr[iface]
            typ    = if2type[iface]

            item = {
                'agent': ip,
                'idx': iface,
                'typ' : typ,
                'status': status,
                'descr': descr,
            }
            insert_interface(conn, 'interfaces_table', item)
        
        if2macs = get_if2mac_table(data, 'BRIDGE-MIB::dot1dTpFdbPort')
        for iface in ifaces :
            if not iface in if2macs:
                continue

            macs = if2macs[iface]
            for mac in macs:
                item = {
                    'agent': ip,
                    'idx'  : iface,
                    'mac'  : mac,
                }
                insert_macaddr(conn, 'macaddrs_table', item)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
