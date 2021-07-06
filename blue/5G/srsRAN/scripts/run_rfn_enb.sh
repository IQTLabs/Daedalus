#!/bin/sh

while [ "$(ip route show default)" = "" ] ; do
	sleep 1
done

ip route del default
ip route add default via 192.168.29.1
exec srsenb $*
