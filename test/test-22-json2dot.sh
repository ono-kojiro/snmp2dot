#!/bin/sh

top_dir="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"

. ./pythonpath.shrc

json2dot="../src/snmp2dot/json2dot.py"

echo "1..1"
jsonfile="output.json"
dotfile="output.dot"
cmd="${json2dot} -o ${dotfile} ${jsonfile}"
echo $cmd
$cmd
if [ "$?" -eq 0 ]; then
  echo "ok"
else
  echo "not ok"
fi

