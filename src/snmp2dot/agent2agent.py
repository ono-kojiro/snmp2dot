import sys

import sqlite3

import logging
logger = logging.getLogger(__name__)

__all__ = [
  "create_agent2agent_view",
]

def create_agent2agent_view(conn):
    view = 'a2a_view'
    c = conn.cursor()

    sql = 'DROP TABLE IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT DISTINCT '
    sql += '  graph_view.sysname AS sysname, '
    sql += '  graph_view.ifidx AS ifidx, '
    sql += '  graph_view.mac AS mac, '
    sql += '  graph_view.ip AS ip, '
    sql += '  interfaces_view.sysname AS dummy '
    sql += 'FROM graph_view '
    sql += 'LEFT OUTER JOIN interfaces_view ON ( '
    sql += '  graph_view.mac = interfaces_view.phys '
    sql += ') '
    sql += 'WHERE ('
    sql += '  dummy IS NOT NULL '
    sql += '  AND graph_view.sysname != interfaces_view.sysname '
    sql += ') '
    sql += 'ORDER BY '
    sql += '  graph_view.sysname ASC, '
    sql += '  graph_view.ifidx ASC, '
    sql += '  graph_view.mac ASC, '
    sql += '  graph_view.ip ASC '
    sql += ';'

    c.execute(sql)

