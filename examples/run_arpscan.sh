#!/bin/sh

logfile="arpscan.arp"

arp_opts=""
arp_opts="${arp_opts} --localnet --ignoredups"
arp_opts="${arp_opts} -ouifile=/usr/share/arp-scan/ieee-oui.txt"
arp_opts="${arp_opts} --macfile=/etc/arp-scan/mac-vendor.txt"

rm -rf ${logfile}

targets="luna2:macvlan0 abaoaqu:macvlan0 trixie:enp1s0"

count=0

for target in $targets; do
  remote=`echo ${target} | sed 's/:.*//'`
  iface=`echo ${target} | sed 's/.*://'`
  echo "DEBUG: run arp-scan in $remote at interface $iface" | tee -a ${logfile}
  ssh -t $remote "/usr/sbin/arp-scan ${arp_opts} --interface $iface" | tee -a ${logfile}
  if [ "$?" -eq 0 ]; then
    echo "ok"
  else
    echo "not ok"
  fi
  count=`expr $count + 1`
done

echo "1..${count}"

