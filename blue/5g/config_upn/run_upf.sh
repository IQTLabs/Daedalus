#!/bin/bash

set -e

hname=$(hostname)
i=0
for ip in $* ; do
	i=$((i+1))
	ifname=ogstap${i}
	if [ "$i" -eq 1 ] ; then
		ifname=ogstap
	fi
	echo ${ifname}: ${ip}
	ip tuntap add name $ifname mode tap
	ip addr add $ip dev $ifname
	ip link set $ifname up
	iptables -I INPUT -i $ifname -j ACCEPT
done

iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

mkdir -p /usr/local/var/log/open5gs
touch /usr/local/var/log/open5gs/${hname}.log
tail -f /usr/local/var/log/open5gs/${hname}.log &
open5gs-upfd -c /usr/local/etc/open5gs/${hname}.yaml
