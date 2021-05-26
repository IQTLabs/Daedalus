#!/bin/sh

ip tuntap add name ogstap mode tap
ip addr add 10.10.0.1/16 dev ogstap
#ip addr add cafe::1/16 dev ogstap
ip link set dev ogstap address 0e:00:00:00:00:ff
ip link set ogstap up

# masquerade
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -I INPUT -i ogstap -j ACCEPT

mkdir -p /usr/local/var/log/open5gs
touch /usr/local/var/log/open5gs/upf.log

tail -f /usr/local/var/log/open5gs/upf.log &

open5gs-upfd -c /usr/local/etc/open5gs/upf.yaml
