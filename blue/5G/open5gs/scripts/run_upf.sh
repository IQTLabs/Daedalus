#!/bin/bash

set -e

/etc/init.d/openvswitch-switch start

i=0
for ip in $* ; do
	i=$((i+1))
	ifname=ogstap${i}
	if [ "$i" -eq 1 ] ; then
		ifname=ogstap
	fi
	echo "${ifname}": "${ip}"
	ip tuntap add name "$ifname" mode tap
        br="${ifname}"br
	ovs-vsctl add-br "$br"
	ovs-vsctl add-port "$br" "$ifname"
	brmac=$(ovs-ofctl dump-ports-desc "$br"|grep LOCAL|grep -Eo '([a-f0-9:]{17,17})$')
	ovs-ofctl del-flows "$br"
	ovs-ofctl add-flow "$br" "in_port=$br,actions=output:$ifname"
	ovs-ofctl add-flow "$br" "in_port=$ifname,,actions=set_field:$brmac->eth_dst,output:$br"
	ip addr add "$ip" dev "$br"
	ip link set "$ifname" up
	ip link set "$br" up
	iptables -I INPUT -i "$br" -j ACCEPT
done

ovs-vsctl show
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

open5gs-upfd -c /usr/local/etc/slice.yaml
