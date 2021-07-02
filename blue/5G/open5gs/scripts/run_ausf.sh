#!/bin/sh

mkdir -p /usr/local/var/log/open5gs
touch /usr/local/var/log/open5gs/ausf.log

tail -f /usr/local/var/log/open5gs/ausf.log &

open5gs-ausfd -c /usr/local/etc/open5gs/ausf.yaml
