#!/bin/sh

top_dir="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"

# load agents variable
. ./agents.shrc

. ./pythonpath.shrc

arp2db="../src/snmp2dot/arp2db.py"

echo "1..2"
jsonfile="arpscan.json"
database="database.db"
cmd="${arp2db} -o ${database} ${jsonfile}"
echo $cmd
$cmd
if [ "$?" -eq 0 ]; then
  echo "ok"
else
  echo "not ok"
fi

sqlite3 ${database} ".dump" > database.sql
if [ "$?" -eq 0 ]; then
  echo "ok"
else
  echo "not ok"
fi

