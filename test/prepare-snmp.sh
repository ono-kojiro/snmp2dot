#!/bin/sh

agents=`cat agents.yml | yq -c -r ".agents.[].name"`

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

vars=""
vars="$vars snmpver seclevel secname"
vars="$vars authprotocol authpassword"
vars="$vars privprotocol privpassword"
vars="$vars ip manager"

count="0"

for agent in $agents; do
  echo "DEBUG: agent is $agent" 1>&2
  . ./common.shrc
  . ./password.shrc

  # overwrite variables from YAML 
  for var in $vars; do
    #echo "DEBUG:   check var '$var'"
    val=`get_attr $agent $var`
    if [ ! -z "$val" ]; then
      echo "DEBUG: overwrite $var = $val" 1>&2
      eval $var="'$val'"
    fi
  done

  ret=0
  # check variables
  for var in ${vars}; do
    val=`eval "echo \\$${var}"`
    if [ -z "$val" ]; then
      echo "ERROR: '${var}' is NOT defined" 1>&2
      ret=`expr $ret + 1`
    fi
  done

  if [ "$ret" -ne 0 ]; then
    exit 1
  fi

  flags=""
  flags="$flags -v $snmpver"
  flags="$flags -l $seclevel"
  flags="$flags -u $secname"
  flags="$flags -a $authprotocol"
  flags="$flags -A $authpassword"
  flags="$flags -x $privprotocol"
  flags="$flags -X $privpassword"
  
  flags="$flags -OX"
  flags="$flags -m $mibs"
  flags="$flags -M $mibdirs"
  flags="$flags -Pe"
  flags="$flags --hexOutputLength=0"

  echo "snmpwalk $flags"
  if [ ! -z "$manager" ]; then
    precmd="ssh -t $manager"
  else
    precmd=""
  fi

  logfile="${agent}.log"
  errfile="${agent}.err"
  rm -f $logfile
  rm -f $errfile

  for oid in $oids; do
    cmd="$precmd snmpwalk $flags ${ip} ${oid}"
    echo "CMD: $cmd" 1>&2
    $cmd >> $logfile 2>> $errfile
    if [ "$?" -eq 0 ]; then
      echo "ok - $cmd"
    else
      echo "not ok - $cmd"
    fi
    count=`expr $count + 1`
  done

done

echo "1..${count}"

