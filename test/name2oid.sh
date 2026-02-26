#!/bin/sh

flags="-m ALL -M /usr/share/snmp/mibs"

for name in "$@" ; do
  snmptranslate $flags -On $name
done

