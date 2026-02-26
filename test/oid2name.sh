#!/bin/sh

miblist="ALL"
dirlist="/usr/share/snmp/cisco-mibs/v1"
dirlist="$dirlist:/usr/share/snmp/cisco-mibs/v2"
flags="-m $miblist -M $dirlist"

for oid in "$@"; do
  snmptranslate $flags -OS $oid
done
