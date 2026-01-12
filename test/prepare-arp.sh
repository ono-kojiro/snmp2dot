#!/bin/sh

logfile="arpscan.log"

arp_opts=""
arp_opts="${arp_opts} --localnet --ignoredups --plain"
arp_opts="${arp_opts} -ouifile=/usr/share/arp-scan/ieee-oui.txt"
arp_opts="${arp_opts} --macfile=/etc/arp-scan/mac-vendor.txt"

echo "1..2"

rm -rf ${logfile}
ssh -t abaoaqu "sudo -E arp-scan ${arp_opts}" >> ${logfile}
if [ "$?" -eq 0 ]; then
  echo "ok"
else
  echo "not ok"
fi

ssh -t solomon "sudo -E arp-scan ${arp_opts}" >> ${logfile}
if [ "$?" -eq 0 ]; then
  echo "ok"
else
  echo "not ok"
fi

