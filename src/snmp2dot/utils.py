import sys

import re
import json
import yaml

import logging
logger = logging.getLogger(__name__)

__all__ = [
  "read_json",
  "read_yaml",
  "setup_logging",
  "recursive_merge",
  "get_mib_data",
  "normalize_mac",
  "get_dict_values",
  "get_scalar_value",
]

def read_json(filepath) :
    with open(filepath, mode='r', encoding='utf-8') as fp :
        data = json.loads(fp.read())
        return data

def read_yaml(filepath):
    fp = open(filepath, mode="r", encoding="utf-8")
    docs = yaml.load_all(fp, Loader=yaml.loader.SafeLoader)

    data = {}
    for doc in docs:
        for key in doc :
            data[key] = doc[key]
    fp.close()
    return data

def setup_logging(logfile, debug):
    fmt = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    if logfile :
        # FileHandler
        handler = logging.FileHandler(logfile, mode='w')
    else :
        handler = logging.StreamHandler(sys.stderr)

    handler.setFormatter(fmt)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)

    if debug :
        root.setLevel(logging.DEBUG)
    else :
        root.setLevel(logging.INFO)

def recursive_merge(dict1, dict2):
    if dict2 is None :
        return dict1

    for key, value in dict2.items():
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
            # If both values are dictionaries, recurse
            recursive_merge(dict1[key], value)
        else:
            # Otherwise, update (or add) the value
            dict1[key] = value
    return dict1


def get_mib_data(data, oidname) :
    # ex. oidname = 'RFC1213-MIB::atNetAddress'
    mibname, objname = re.split(r'::', oidname)
    
    res = data.get(mibname, None)
    if res is None:
        return res

    res = res.get(objname, None)
    return res

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
        print("ERROR: invalid mac address, '{0}'".format(mac_str))
        sys.exit(1)

    return mac


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

