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
            'sysobjectid' : row['sysobjectid'],
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
