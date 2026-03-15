#!/usr/bin/env python3

import sys

import getopt
import json

import shlex
import subprocess

import yaml
import copy

from pprint import pprint

def usage():
    print("Usage : {0}".format(sys.argv[0]))

def read_json(filepath) :
    with open(filepath, mode='r', encoding='utf-8') as fp :
        data = json.loads(fp.read())
        return data

def read_yaml(filepath):
    fp = open(filepath, mode="r", encoding="utf-8")
    docs = yaml.load_all(fp, Loader=yaml.loader.SafeLoader)
    configs = {}
    for doc in docs:
        configs = configs | doc
    fp.close()
    return configs

def main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hvo:c:p:",
            [
                "help",
                "version",
                "output=",
                "config=",
                "passwd=",
            ]
        )
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)
    
    output = None
    config_yml = None
    passwd_yml = None
	
    for o, a in opts:
        if o == "-v":
            usage()
            sys.exit(0)
        elif o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-o", "--output"):
            output = a
        elif o in ("-c", "--config"):
            config_yml = a
        elif o in ("-p", "--passwd"):
            passwd_yml = a
        else:
            assert False, "unknown option"
	
    ret = 0

    if output is not None :
        fp = open(output, mode='w', encoding='utf-8')
    else :
        fp = sys.stdout
	
    if ret != 0:
        sys.exit(1)

    configs = read_yaml(config_yml)
    pprint(configs)
    
    passwds = read_yaml(passwd_yml)

    agents = configs['agents']
    default_vars = configs['default']
    pprint(agents)

    for agent in args:
        print('DEBUG: {0}'.format(agent), file=sys.stderr)
        config = copy.deepcopy(default_vars)
        pprint(config)
        config = config | configs['agents'][agent]

        if 'default' in passwds:
            config = config | passwds['default']
        if agent in passwds:
            config = config | passwds[agent]

        manager = config['manager']

        flags  = ''
        flags += ' -v {0}'.format(config['snmpver'])
        flags += ' -l {0}'.format(config['seclevel'])
        flags += ' -u {0}'.format(config['secname'])
        flags += ' -a {0}'.format(config['authprotocol'])
        flags += ' -A {0}'.format(config['authpassword'])
        flags += ' -x {0}'.format(config['privprotocol'])
        flags += ' -X {0}'.format(config['privpassword'])
        flags += ' -OX'
        flags += ' -m {0}'.format(configs['mibs'])
        flags += ' -M {0}'.format(configs['mibdirs'])
        flags += ' -Pe'
        flags += ' --hexOutputLength=0'

        flags += ' {0}'.format(config['ip'])

        for oid in configs['oids']:
            cmd = 'ssh {0} snmpwalk {1} {2}'.format(manager, flags, oid)
            fp.write('# CMD: {0}\n'.format(cmd))
        
            cmds = shlex.split(cmd)
            print('DEBUG: {0}'.format(cmds), file=sys.stderr)

            proc = subprocess.Popen(
                 cmds,
                 stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE,
                 text=True,
                 bufsize=1,
            )

            for line in proc.stdout:
                fp.write('{0}\n'.format(line.strip()))

            proc.wait()

    if output is not None :
        fp.close()

if __name__ == '__main__' :
    main()

