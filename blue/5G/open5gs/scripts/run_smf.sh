#!/bin/sh

mkdir -p /usr/local/var/log/open5gs
touch /usr/local/var/log/open5gs/smf.log

tail -f /usr/local/var/log/open5gs/smf.log &

if [ -z "$1" ]
then
	open5gs-smfd -c /usr/local/etc/open5gs/smf.yaml
else
	open5gs-smfd -c /usr/local/etc/open5gs/smf5gc.yaml
fi
