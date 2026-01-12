#!/bin/sh

# load agents variable
. ./agents.shrc

oids=" \
  SNMPv2-MIB::sysDescr \
  IF-MIB::ifDescr \
  IF-MIB::ifOutOctets \
  IF-MIB::ifInOctets \
  IF-MIB::ifTable \
  IF-MIB::interfaces \
  IP-MIB::ip \
  BRIDGE-MIB::dot1dBridge \
"

mibs="ALL"
mibdirs="/usr/share/snmp/mibs"

count="0"

for agent in ${agents}; do
  rm -f ${agent}.log
  rm -f ${agent}.err

  if [ ! -e "./${agent}.shrc" ]; then
    echo "ERROR: no ${agent}.shrc file for agent ${agent}" 1>&2
    continue
  fi

  for oid in ${oids}; do
    opts=""
    opts="${opts} --agent ${agent}"
    opts="${opts} --mibs ${mibs}"
    opts="${opts} --mibdirs ${mibdirs}"
    opts="${opts} --oid ${oid}"
    #echo "opts is ${opts}" 1>&2
    ./snmpretrieve.sh ${opts} 2>>${agent}.err >> ${agent}.log
    if [ "$?" -eq 0 ]; then
      echo "ok"
    else
      echo "not ok"
    fi
    count=`expr $count + 1`
  done
done

echo "1..${count}"



