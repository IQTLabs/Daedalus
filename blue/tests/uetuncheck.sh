#!/bin/bash

UECON=$1
UETUN=$2

echo "waiting for ${UECON} tunnel to come up..."
i=0
OUT=""
while [ "$OUT" == "" ] && [ "$i" != 300 ] ; do
	echo -n .
	OUT=$(docker exec "${UECON}" ip link|grep "${UETUN}")
	((i=i+1))
	sleep 1
done
docker logs "${UECON}"

if [ "$OUT" == "" ] ; then
	echo no "${UETUN}"
	exit 1
fi

echo "checking ${UECON} connectivity..."
docker exec "${UECON}" wget -q -O- bing.com
