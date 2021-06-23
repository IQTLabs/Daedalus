#!/bin/bash

set -e

host=$(hostname)
/etc/init.d/openvswitch-switch start

i=0
for ip in $* ; do
	i=$((i+1))
	ifname=ogstap${i}
	if [ "$i" -eq 1 ] ; then
		ifname=ogstap
	fi
	echo ${ifname}: ${ip}
	ip tuntap add name $ifname mode tap
        br=${ifname}br
	ovs-vsctl add-br $br
	ovs-vsctl add-port $br $ifname
	# TODO: workaround trailing nulls in OGS response, with in-OVS ARP responder.
	brmac=$(ovs-ofctl dump-ports-desc $br|grep LOCAL|grep -Eo '([a-f0-9:]{17,17})$')
	ovs-ofctl del-flows $br
	ovs-ofctl add-flow $br "in_port=$br,arp,actions=move:NXM_OF_ARP_TPA[]->NXM_NX_REG0[],load:0x2->NXM_OF_ARP_OP[0..2],move:NXM_OF_ETH_SRC[]->NXM_OF_ETH_DST[],move:NXM_NX_ARP_SHA[]->NXM_NX_ARP_THA[],move:NXM_OF_ARP_SPA[]->NXM_OF_ARP_TPA[],move:NXM_NX_REG0[]->NXM_OF_ARP_SPA[],set_field:0e:00:00:00:00:01->eth_src,set_field:0e:00:00:00:00:01->arp_sha,IN_PORT"
	ovs-ofctl add-flow $br "in_port=$br,ip,actions=output:$ifname"
	ovs-ofctl add-flow $br "in_port=$ifname,ip,actions=set_field:$brmac->eth_dst,output:$br"
	ip addr add $ip dev $br
	ip link set $ifname up
	ip link set $br up
	iptables -I INPUT -i $br -j ACCEPT
done

ovs-vsctl show
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

mkdir -p /usr/local/var/log/open5gs
touch /usr/local/var/log/open5gs/${host}.log
tail -f /usr/local/var/log/open5gs/${host}.log &
open5gs-upfd -c /usr/local/etc/open5gs/${host}.yaml
