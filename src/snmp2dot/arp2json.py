#!/usr/bin/env python3

import sys
import re

import getopt
import yaml

from pprint import pprint
import json

import ipaddress

import snmp2dot

def version():
    print('{0}'.format(snmp2dot.__version__))

def usage():
    print("Usage : {0}".format(sys.argv[0]))

def read_json(jsonfile) :
    fp = open(jsonfile, mode='r', encoding='utf-8')
    data = json.load(fp)
    fp.close()
    return data

def is_valid_ipv4(addr) :
    try :
        ipaddress.IPv4Address(addr)
        return True
    except :
        return False

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
    
    if output is not None:
        fp = open(output, mode="w", encoding="utf-8")
    else :
        fp = sys.stdout

    if ret != 0:
        sys.exit(1)
   
    mac2ip = {}

    for filepath in args:
        fp_in = open(filepath, mode='r', encoding='utf-8')
        while True:
            line = fp_in.readline()
            if not line :
                break

            line = re.sub(r'\r?\n?$', '', line)

            ipv4p = r'(([0-9]{1,3}\.){3}[0-9]{1,3})'
            macp  = r'(([0-9a-f]{2}:){5}[0-9a-f]{2})'
            m = re.search(r'^' + ipv4p + r'\s+' + macp + r'\s+(.+)', line)
            if m :
                ip = m.group(1)
                mac = m.group(3)
                vendor = m.group(5)
                if is_valid_ipv4(ip) :
                    mac2ip[mac] = {
                        'ip' : ip,
                        'vendor' : vendor,
                    }

            m = re.search(r' MAC: ' + macp + r', IPv4: ' + ipv4p, line)
            if m :
                mac = m.group(1)
                ip  = m.group(3)
                vendor = '(arp-scan host)'
                if is_valid_ipv4(ip) :
                    mac2ip[mac] = {
                        'ip' : ip,
                        'vendor' : vendor,
                    }

        fp_in.close()

    #yaml.dump(data,
    #    fp,
    #    allow_unicode=True,
    #    default_flow_style=False,
    #    sort_keys=True,
    #)

    fp.write(
        json.dumps(
            {
                "arp-scan" : mac2ip,
            },
            indent=4,
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    
    fp.write('\n')

    if output is not None:
        fp.close()

if __name__ == "__main__":
    main()

