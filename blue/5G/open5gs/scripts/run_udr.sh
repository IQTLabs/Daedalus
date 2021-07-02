#!/bin/sh

until mongo  --host ${DB_HOST} --eval "print(\"waited for connection\")" 2>&1 >/dev/null
  do
    sleep 5
    echo "Trying to connect to MongoDB"
  done

echo "Launching UDR..."

mkdir -p /usr/local/var/log/open5gs
touch /usr/local/var/log/open5gs/udr.log

tail -f /usr/local/var/log/open5gs/udr.log &

open5gs-udrd -c /usr/local/etc/open5gs/udr.yaml
