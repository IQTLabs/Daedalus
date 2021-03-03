#!/bin/sh

TUN=tun_srsue

while ! grep -q $TUN /proc/net/dev ; do
	sleep 1
done

ip route del default

while [ "$(ip route show default)" = "" ] ; do
	ip route add default dev $TUN
	sleep 1
done

exit 0
