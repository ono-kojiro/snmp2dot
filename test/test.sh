#!/bin/sh

SNMPCONFPATH=`pwd`/snmpconf

OID="sysName"

MIBDIRS=`pwd`/mibs:/usr/share/snmp/mibs
#MIBDIRS=`pwd`/mibs
MIBS="ALL"

cmd="env SNMPCONFPATH=${SNMPCONFPATH} MIBDIRS=${MIBDIRS} MIBS=${MIBS}"
cmd="$cmd snmpwalk 192.168.1.252 $OID"
echo $cmd

$cmd | tee 192.168.1.252.snmp





