#!/bin/sh

logfile="arpscan.log"

arp_opts=""
arp_opts="${arp_opts} --localnet --ignoredups --plain"
arp_opts="${arp_opts} -ouifile=/usr/share/arp-scan/ieee-oui.txt"
arp_opts="${arp_opts} --macfile=/etc/arp-scan/mac-vendor.txt"


count=0

rm -rf ${logfile}
ssh -t abaoaqu "sudo -E arp-scan ${arp_opts}" >> ${logfile}
if [ "$?" -eq 0 ]; then
  echo "ok"
else
  echo "not ok"
fi
count=`expr $count + 1`

ssh -t solomon "sudo -E arp-scan ${arp_opts}" >> ${logfile}
if [ "$?" -eq 0 ]; then
  echo "ok"
else
  echo "not ok"
fi
count=`expr $count + 1`

ssh -t xubuntu "sudo -E arp-scan ${arp_opts}" >> ${logfile}
if [ "$?" -eq 0 ]; then
  echo "ok"
else
  echo "not ok"
fi
count=`expr $count + 1`

echo "1..${count}"

