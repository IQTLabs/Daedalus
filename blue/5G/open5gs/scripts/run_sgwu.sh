#!/bin/bash

host=$(hostname)
echo "Launching ${host}..."

touch /usr/local/var/log/open5gs/${host}.log

open5gs-sgwud -c /usr/local/etc/open5gs/${host}.yaml
