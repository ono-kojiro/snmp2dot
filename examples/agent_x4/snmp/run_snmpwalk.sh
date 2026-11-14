#!/bin/sh

for arg in "$@"; do
  echo "$arg" | grep -Eq '^REMOTE_AGENTS='
  if [ $? -eq 0 ]; then
	remote_agents=`echo $arg | sed 's/.*=//'`
  fi
done

for remote_agent in $remote_agents; do
  remote=`echo $remote_agent | sed 's/\-.*//'`
  agent=`echo $remote_agent | sed 's/.*\-//'`
 
  output="${remote}-${agent}.snmp"
  if [ ! -e "$output" ]; then
    echo "OUTPUT: $output"
    ssh -t $remote "snmpwalk $agent" | tee $output
  else
    echo "SKIP: $output"
  fi
done
