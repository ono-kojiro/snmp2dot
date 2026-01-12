#!/bin/sh

top_dir="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"

# load agents variable
. ./agents.shrc

. ./pythonpath.shrc

snmp2db="../src/snmp2dot/snmp2db.py"

jsonfiles=""
for agent in ${agents}; do
  jsonfiles="${jsonfiles} ${agent}.json"
done

echo "1..2"

${snmp2db} -o database.db ${jsonfiles}
if [ "$?" -eq 0 ]; then
  echo "ok"
else
  echo "not ok"
fi

sqlite3 database.db ".dump" > database.sql
if [ "$?" -eq 0 ]; then
  echo "ok"
else
  echo "not ok"
fi

