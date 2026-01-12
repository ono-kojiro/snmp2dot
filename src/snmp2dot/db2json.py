#!/usr/bin/env python3

import sys

import getopt
import json

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

def get_agents(conn) :
    c = conn.cursor()
    sql = 'SELECT * FROM agents_view;'
    
    items = []
    rows = c.execute(sql)
    for row in rows :
        item = {
            'ip' : row['ip'],
            'mac' : row['mac'],
            'sysdescr' : row['sysdescr'],
        }
        items.append(item)

    return items

def get_connections_view(conn) :
    c = conn.cursor()
    sql = 'SELECT * FROM connections_view;'
    
    items = []
    rows = c.execute(sql)
    for row in rows :
        item = {
            'agent' : row['src_ip'],
            'idx'   : row['src_port'],
            'mac'   : row['dst_mac'],
            'ip'    : row['dst_ip'],
        }
        items.append(item)

    return items

def get_a2a_view(conn) :
    c = conn.cursor()
    sql = 'SELECT * FROM a2a_view;'
    
    items = []
    rows = c.execute(sql)
    for row in rows :
        item = {
            'src_ip'   : row['src_ip'],
            'src_port'  : row['src_port'],
            'dst_mac'  : row['dst_mac'],
            'dst_ip'  : row['dst_ip'],
        }
        items.append(item)

    return items

def get_a2t_view(conn) :
    c = conn.cursor()
    sql = 'SELECT * FROM a2t_view;'
    
    items = []
    rows = c.execute(sql)
    for row in rows :
        item = {
            'src_ip'   : row['src_ip'],
            'src_port'  : row['src_port'],
            'dst_mac'  : row['dst_mac'],
            'dst_ip'  : row['dst_ip'],
        }
        items.append(item)

    return items

def create_agents_view(conn, view):
    c = conn.cursor()

    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT '
    sql += '  DISTINCT ip, mac, sysdescr '
    sql += 'FROM agents_table '
    sql += ';'

    c.execute(sql)

def create_connections_view(conn, view):
    c = conn.cursor()

    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT '
    #sql += '  interfaces_table.agent AS agent_ip, '
    sql += '  agents_table.ip  AS src_ip, '
    sql += '  agents_table.mac AS src_mac, '
    sql += '  interfaces_table.idx AS src_port, '
    sql += '  macaddrs_table.mac AS dst_mac, '
    sql += '  arp_table.ip AS dst_ip '
    sql += 'FROM interfaces_table '
    sql += 'LEFT OUTER JOIN macaddrs_table '
    sql += '  ON interfaces_table.idx = macaddrs_table.idx '
    sql += 'LEFT OUTER JOIN arp_table '
    sql += '  ON macaddrs_table.mac = arp_table.mac '
    sql += 'LEFT OUTER JOIN agents_table '
    sql += '  ON interfaces_table.agent = agents_table.ip '
    sql += 'WHERE '
    sql += '  status = "up(1)" '
    sql += '  AND macaddrs_table.mac != "" '
    #sql += '  AND agents_table.sysdescr IS NULL '
    sql += ';'

    c.execute(sql)

def create_a2a_view(conn, view):
    c = conn.cursor()

    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT '
    sql += '  macaddrs_table.agent AS src_ip, '
    sql += '  macaddrs_table.idx   AS src_port, '
    sql += '  macaddrs_table.mac   AS dst_mac, '
#    sql += '  src_table.sysdescr   AS sysdescr, '
#    sql += '  dst_table.ip         AS dst_ip, '
#    sql += '  dst_table.mac        AS dst_mac, '
    sql += '  arp_table.ip         AS dst_ip, '
    sql += '  dst_table.sysdescr   AS dst_descr '
    sql += 'FROM macaddrs_table '
    sql += 'LEFT OUTER JOIN agents_table AS src_table '
    sql += '  ON macaddrs_table.agent = src_table.ip '
    sql += 'LEFT OUTER JOIN agents_table AS dst_table '
    sql += '  ON macaddrs_table.mac = dst_table.mac '
    sql += 'LEFT OUTER JOIN arp_table '
    sql += '  ON macaddrs_table.mac = arp_table.mac '
    sql += 'WHERE '
    sql += '  dst_table.sysdescr IS NOT NULL '
    sql += ';'

    c.execute(sql)

def create_a2t_view(conn, view):
    c = conn.cursor()

    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT '
    sql += '  macaddrs_table.agent AS src_ip, '
    sql += '  macaddrs_table.idx   AS src_port, '
    sql += '  macaddrs_table.mac   AS dst_mac, '
    sql += '  arp_table.ip         AS dst_ip '
    sql += 'FROM macaddrs_table '
    sql += 'LEFT OUTER JOIN a2a_view '
    sql += '  ON  macaddrs_table.agent = a2a_view.src_ip '
    sql += '  AND macaddrs_table.idx   = a2a_view.src_port '
    sql += 'LEFT OUTER JOIN arp_table '
    sql += '  ON macaddrs_table.mac = arp_table.mac '
    sql += 'WHERE '
    sql += '  a2a_view.dst_descr IS NULL '
    sql += ';'

    c.execute(sql)


def main():
    ret = 0

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
	
    if output is not None :
        fp = open(output, mode='w', encoding='utf-8')
    else :
        fp = sys.stdout
	
    if ret != 0:
        sys.exit(1)

    data = {}

    for database in args:
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row
    
        create_agents_view(conn, 'agents_view')
        create_connections_view(conn, 'connections_view')
        create_a2a_view(conn, 'a2a_view')
        create_a2t_view(conn, 'a2t_view')

        agents = get_agents(conn)
        data['agents'] = agents
        
        a2a = get_a2a_view(conn)
        data['agent2agent'] = a2a
        
        a2t = get_a2t_view(conn)
        data['agent2terminal'] = a2t

    fp.write(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False,
        )
    )
    fp.write('\n')

    if output is not None :
        fp.close()

if __name__ == "__main__":
    main()
