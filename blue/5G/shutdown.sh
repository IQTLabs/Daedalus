#!/bin/bash

DCFS=/tmp/d5g-dockerfiles.txt

if [ -f "$DCFS" ] ; then
       docker-compose $(cat ${DCFS}) down --remove-orphans
fi
for network in cpn upn ran rfn ; do docker network rm $network ; done
cd dovesnap && docker-compose -f docker-compose.yml -f docker-compose-standalone.yml down --remove-orphans && cd ..
for volume in core_mongodb_data dovesnap_ovs-data ; do docker volume rm -f $volume ; done
