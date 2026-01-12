#!/bin/sh

top_dir="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"

# load agents variable
. ./agents.shrc

. ./pythonpath.shrc

arp2json="../src/snmp2dot/arp2json.py"

echo "1..1"
logfile="arpscan.log"
jsonfile="arpscan.json"
cmd="${arp2json} -o ${jsonfile} ${logfile}"
echo $cmd
$cmd
if [ "$?" -eq 0 ]; then
  echo "ok"
else
  echo "not ok"
fi

