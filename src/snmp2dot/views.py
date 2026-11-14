import sys

import sqlite3

import logging
logger = logging.getLogger(__name__)

__all__ = [
  'create_a2t_edges_view',
  'create_a2a_edges_view',
]

def create_a2t_edges_view(conn):
    view = 'a2t_edges_view'
    c = conn.cursor()

    sql = 'DROP TABLE IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT DISTINCT '
    sql += '  graph_view.sysname AS sysname, '
    sql += '  graph_view.ifidx AS ifidx, '
    sql += '  graph_view.mac AS mac, '
    sql += '  graph_view.ip AS ip, '
    sql += '  agents_view.default_ifidx AS default_ifidx, '
    sql += '  a2a_view.sysname AS dummy1, '
    sql += '  a2a_view.ifidx AS dummy2 '
    sql += 'FROM graph_view '
    sql += 'LEFT OUTER JOIN agents_view ON ( '
    sql += '  graph_view.sysname = agents_view.sysname '
    sql += ') '
    sql += 'LEFT OUTER JOIN a2a_view ON ( '
    sql += '  graph_view.sysname = a2a_view.sysname AND '
    sql += '  graph_view.ifidx = a2a_view.ifidx '
    sql += ') '
    sql += 'WHERE dummy1 IS NULL '
    sql += 'ORDER BY sysname ASC, ifidx ASC, mac ASC, ip ASC '
    sql += ';'

    c.execute(sql)

def create_a2a_edges_view(conn):
    view = 'a2a_edges_view'
    c = conn.cursor()

    sql = 'DROP TABLE IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT DISTINCT '
    sql += '  graph_view.sysname AS sysname, '
    sql += '  graph_view.ifidx AS ifidx, '
    sql += '  graph_view.mac AS mac, '
    sql += '  graph_view.ip AS ip, '
    sql += '  agents_view.default_ifidx AS default_ifidx, '
    sql += '  interfaces_view.sysname AS dst_sysname, '
    sql += '  interfaces_view.idx AS dst_ifidx, '
    sql += '  a2a_view.sysname AS dummy1, '
    sql += '  a2a_view.ifidx AS dummy2 '
    sql += 'FROM graph_view '
    sql += 'LEFT OUTER JOIN agents_view ON ( '
    sql += '  graph_view.sysname = agents_view.sysname '
    sql += ') '
    sql += 'LEFT OUTER JOIN interfaces_view ON ( '
    sql += '  graph_view.mac = interfaces_view.phys '
    sql += ') '
    sql += 'LEFT OUTER JOIN a2a_view ON ( '
    sql += '  graph_view.sysname = a2a_view.sysname AND '
    sql += '  graph_view.ifidx = a2a_view.ifidx '
    sql += ') '
    sql += 'WHERE ('
    sql += '  graph_view.sysname != dst_sysname AND '
    sql += '  dummy1 IS NOT NULL '
    sql += ') '
    sql += 'ORDER BY sysname ASC, ifidx ASC, mac ASC, ip ASC '
    sql += ';'

    c.execute(sql)

