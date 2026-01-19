#!/bin/sh

logfile="arpscan.log"

arp_opts=""
arp_opts="${arp_opts} --localnet --ignoredups --plain"
arp_opts="${arp_opts} -ouifile=/usr/share/arp-scan/ieee-oui.txt"
arp_opts="${arp_opts} --macfile=/etc/arp-scan/mac-vendor.txt"



rm -rf ${logfile}

#clients="abaoaqu solomon xubuntu"
clients="xubuntu"

count=0

for client in $clients; do
  ssh -t $client "sudo -E arp-scan ${arp_opts}" >> ${logfile}
  if [ "$?" -eq 0 ]; then
    echo "ok"
  else
    echo "not ok"
  fi
  count=`expr $count + 1`
done

echo "1..${count}"

