#!/bin/sh

top_dir="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"

# load agents variable
. ./agents.shrc

. ./pythonpath.shrc

snmp2json="../src/snmp2dot/snmp2json.py"

echo "1..3"

got=`${snmp2json} --version`
exp='0.0.1'
if [ "$got" = "$exp" ]; then
  echo "ok - version $got"
else
  echo "not ok - $got != $exp"
fi

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

