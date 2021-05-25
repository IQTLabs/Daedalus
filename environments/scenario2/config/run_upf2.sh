#!/bin/sh

ip tuntap add name ogstap mode tap
ip addr add 10.11.0.1/16 dev ogstap
ip link set dev ogstap address 0e:00:00:00:00:ff
ip link set ogstap up

# masquerade
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -I INPUT -i ogstap -j ACCEPT

mkdir -p /usr/local/var/log/open5gs
touch /usr/local/var/log/open5gs/upf2.log

tail -f /usr/local/var/log/open5gs/upf2.log &

open5gs-upfd -c /usr/local/etc/open5gs/upf2.yaml
