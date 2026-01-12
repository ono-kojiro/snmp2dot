#!/bin/sh

top_dir="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"

. ./pythonpath.shrc

db2json="../src/snmp2dot/db2json.py"

echo "1..1"
database="database.db"
jsonfile="output.json"
cmd="${db2json} -o ${jsonfile} ${database}"
echo $cmd
$cmd
if [ "$?" -eq 0 ]; then
  echo "ok"
else
  echo "not ok"
fi

