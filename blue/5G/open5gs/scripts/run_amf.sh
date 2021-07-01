#!/bin/sh

mkdir -p /usr/local/var/log/open5gs
touch /usr/local/var/log/open5gs/amf.log

tail -f /usr/local/var/log/open5gs/amf.log &

open5gs-amfd -c /usr/local/etc/open5gs/amf.yaml
