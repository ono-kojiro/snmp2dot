#!/usr/bin/env python3

import sys
import re

import getopt
import yaml

from pprint import pprint
import json

import ipaddress

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
            m = re.search(r'^(\S+)\s+(\S+)\s+(.+)', line)
            if m :
                ip = m.group(1)
                mac = m.group(2)
                vendor = m.group(3)
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

