#!/bin/sh

until mongo  --host ${DB_HOST} --eval "print(\"waited for connection\")" 2>&1 >/dev/null
  do
    sleep 5
    echo "Trying to connect to MongoDB"
  done

echo "Launching WebUI..."

npm run start --prefix /open5gs/webui
