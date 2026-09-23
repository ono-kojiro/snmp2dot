#!/bin/sh

arp_opts=""
arp_opts="${arp_opts} --localnet --ignoredups"
arp_opts="${arp_opts} -ouifile=/usr/share/arp-scan/ieee-oui.txt"
arp_opts="${arp_opts} --macfile=/etc/arp-scan/mac-vendor.txt"

for arg in "$@"; do
  echo "$arg" | grep -Eq '^REMOTE_IFACES='
  if [ $? -eq 0 ]; then
	remote_ifaces=`echo $arg | sed 's/.*=//'`
  fi
done

for remote_iface in $remote_ifaces; do
  remote=`echo $remote_iface | sed 's/\-.*//'`
  iface=`echo $remote_iface | sed 's/.*\-//'`
 
  output="${remote}-${iface}.arp"
  if [ ! -e "$output" ]; then
    echo "OUTPUT: $output"
    ssh -t $remote "/usr/sbin/arp-scan ${arp_opts} --interface $iface" | tee $output
    #ssh -t $remote "/usr/sbin/arp-scan ${arp_opts} --interface $iface" | tee $output
  else
    echo "SKIP: $output"
  fi
done

