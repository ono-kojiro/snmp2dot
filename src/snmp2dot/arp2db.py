#!/usr/bin/env python3

import sys

import getopt
import json

import sqlite3

def usage():
    print("Usage : {0}".format(sys.argv[0]))

def read_json(filepath) :
    with open(filepath, mode='r', encoding='utf-8') as fp :
        data = json.loads(fp.read())
        return data

def create_arp_table(conn, table):
    c = conn.cursor()

    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'ip TEXT, '
    sql += 'mac TEXT, '
    sql += 'vendor TEXT '
    sql += ');'

    c.execute(sql)

def create_arp_table(conn, table):
    c = conn.cursor()

    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'ip TEXT, '
    sql += 'mac TEXT, '
    sql += 'vendor TEXT '
    sql += ');'

    c.execute(sql)

def insert_arp(conn, table, item):
    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ?);'.format(table)
    lst = [
        item['ip'],
        item['mac'],
        item['vendor'],
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
        if o == "-v":
            usage()
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
    create_arp_table(conn, 'arp_table')

    for jsonfile in args:
        data = read_json(jsonfile)
        mac2ip = data['arp-scan']
        for mac in mac2ip :
            ip = mac2ip[mac]['ip']
            vendor = mac2ip[mac]['vendor']

            item = {
                'ip': ip,
                'mac': mac,
                'vendor': vendor,
            }
            insert_arp(conn, 'arp_table', item)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
