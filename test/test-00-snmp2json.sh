#!/bin/sh

top_dir="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"

# load agents variable
. ./agents.shrc

. ./pythonpath.shrc

snmp2json="../src/snmp2dot/snmp2json.py"

echo "1..2"
for agent in ${agents}; do
  logfile="${agent}.log"
  jsonfile="${agent}.json"
  cmd="${snmp2json} -o ${jsonfile} ${logfile}"
  echo $cmd
  $cmd
  if [ "$?" -eq 0 ]; then
    echo "ok"
  else
    echo "not ok"
  fi
done

