#!/bin/sh

# database export reference
#mongoexport  --host  ${DB_HOST} --db open5gs --collection subscribers -o /tmp/imsis.json --jsonArray

if [ -n "${DB_HOST}" ]; then
  echo "Database variable found"
else
  echo "Database variable not found, using default one"
  DB_HOST=mongodb
fi

until mongo  --host "${DB_HOST}" --eval "print(\"waited for connection\")" 2>&1 >/dev/null
  do
    sleep 5
    echo "Trying to connect to MongoDB"
  done

mongoimport --host "${DB_HOST}" --db open5gs --authenticationDatabase admin --username "${DB_USER}" --password "${DB_PASS}" --collection subscribers --file /tmp/imsis.json --type json  --jsonArray
sleep infinity
