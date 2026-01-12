#!/bin/sh

top_dir="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"

. ./pythonpath.shrc

createview="../src/snmp2dot/createview.py"

echo "1..2"
database="database.db"
cmd="${createview} -o ${database}"
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

