#!/bin/sh

ip tuntap add name ogstap mode tap
ip addr add 10.11.0.1/16 dev ogstap
ip link set ogstap up
ip tuntap add name ogstap2 mode tap
ip addr add 10.12.0.1/16 dev ogstap2
ip link set ogstap2 up

# masquerade
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -I INPUT -i ogstap -j ACCEPT
iptables -I INPUT -i ogstap2 -j ACCEPT

mkdir -p /usr/local/var/log/open5gs
touch /usr/local/var/log/open5gs/upf2.log

tail -f /usr/local/var/log/open5gs/upf2.log &

open5gs-upfd -c /usr/local/etc/open5gs/upf2.yaml
