#!/bin/sh

logfile="arpscan.log"

arp_opts=""
arp_opts="${arp_opts} --localnet --ignoredups"
arp_opts="${arp_opts} -ouifile=/usr/share/arp-scan/ieee-oui.txt"
arp_opts="${arp_opts} --macfile=/etc/arp-scan/mac-vendor.txt"

rm -rf ${logfile}

echo "INFO: read clients from clients.yml"
clients=`cat clients.yml | yq -c -r ".clients.[]"`

count=0

for client in $clients; do
  ssh -q -t $client "sudo -E arp-scan ${arp_opts}" >> ${logfile}
  if [ "$?" -eq 0 ]; then
    echo "ok"
  else
    echo "not ok"
  fi
  count=`expr $count + 1`
done

echo "INFO: output ${logfile}"
echo "1..${count}"

