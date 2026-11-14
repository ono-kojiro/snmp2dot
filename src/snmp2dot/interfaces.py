import sqlite3

from .utils import *

table = 'interfaces_table'

def create_interfaces_table(conn):
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

def create_interfaces_view(conn):
    view = 'interfaces_view'
    c = conn.cursor()

    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT '
    sql += '  sysname, '
    sql += '  idx, '
    sql += '  phys '
    sql += 'FROM interfaces_table '
    sql += 'WHERE ('
    sql += '  status = "up(1)" '
    sql += '  AND phys != "" '
    sql += ')'
    sql += ';'

    c.execute(sql)

def insert_interface(conn, item):
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
        
def build_interfaces_table(conn, data):
    sysname  = get_scalar_value(data, 'SNMPv2-MIB::sysName.0')

    ifaces = get_dict_values(data, 'IF-MIB::ifIndex')
    if2status = get_dict_values(data, 'IF-MIB::ifOperStatus')
    if2descr  = get_dict_values(data, 'IF-MIB::ifDescr')
    if2type   = get_dict_values(data, 'IF-MIB::ifType')
    if2phys = get_dict_values(data, 'IF-MIB::ifPhysAddress')
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
        insert_interface(conn, item)


