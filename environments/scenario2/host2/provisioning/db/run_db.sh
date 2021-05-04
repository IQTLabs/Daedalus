#!/bin/sh

# database export reference
#mongoexport  --host  ${DB_HOST} --db open5gs --collection subscribers -o /tmp/imsi1.json --jsonArray

if [ -n "${DB_HOST}" ]; then
  echo "Database variable found"
else
  echo "Database variable not found, using default one"
  DB_HOST=mongodb
fi

until mongo  --host ${DB_HOST} --eval "print(\"waited for connection\")" 2>&1 >/dev/null
  do
    sleep 5
    echo "Trying to connect to MongoDB"
  done

mongoimport --host ${DB_HOST} --db open5gs --authenticationDatabase admin --username ${DB_USER} --password ${DB_PASS} --collection subscribers --file /tmp/imsi1.json --type json  --jsonArray
/usr/src/build/examples/ssh_server_fork --hostkey=/etc/ssh/ssh_host_rsa_key --ecdsakey=/etc/ssh/ssh_host_ecdsa_key --dsakey=/etc/ssh/ssh_host_dsa_key --rsakey=/etc/ssh/ssh_host_rsa_key -p 22 0.0.0.0
