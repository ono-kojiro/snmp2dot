import sys

import sqlite3

import logging
logger = logging.getLogger(__name__)

table = 'sysnames_table'

def create_sysnames_table(conn):
    c = conn.cursor()

    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'sysname TEXT '
    sql += ');'

    c.execute(sql)

def insert_sysname(conn, sysname):
    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ? );'.format(table)
    lst = [
        sysname,
    ]

    c.execute(sql, lst)

def get_sysname_id(conn, sysname):
    res = []

    c = conn.cursor()
    sql = 'SELECT id FROM {0} '.format(table)
    sql += 'WHERE sysname = "?" '.format(sysname)
    sql += ';'

    lst = [
        sysname,
    ]

    rows = c.execute(sql, lst)
    for row in rows:
        sysname_id = row[0]
        res.append(sysname_id)

    return res

