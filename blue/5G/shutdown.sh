#!/bin/bash

docker-compose $(cat /tmp/d5g-dockerfiles.txt) down --remove-orphans
for network in cpn upn ran rfn ; do docker network rm $network ; done
cd dovesnap && docker-compose -f docker-compose.yml -f docker-compose-standalone.yml down && cd ..
for volume in nsa_mongodb_data dovesnap_ovs-data ; do docker volume rm $volume ; done
