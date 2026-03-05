#!/bin/sh

oids=" \
  SNMPv2-MIB::sysDescr \
  SNMPv2-MIB::sysObjectID \
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

get_attr()
{
  agent="$1"
  attr="$2"
  res=`cat agents.yml \
    | yq -c -r ".agents.[] | select(.name == \"$agent\") | .$attr"`
  if [ "$res" = "null" ]; then
    res=""
  fi
  echo "$res"
}

agents=`cat agents.yml | yq -c -r ".agents.[].name"`

for agent in ${agents}; do
  rm -f ${agent}.log
  rm -f ${agent}.err

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



