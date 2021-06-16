#!/bin/bash

DC_YAML=""
for dc in docker-compose-5g-nsa-* ; do echo $dc ; DC_YAML="$DC_YAML -f $dc" ; done
docker-compose $DC_YAML down --remove-orphans
for network in cpn upn enb rfn ; do docker network rm $network ; done
cd dovesnap && docker-compose -f docker-compose.yml -f docker-compose-standalone.yml down && cd ..
for volume in 5g_mongodb_data dovesnap_ovs-data ; do docker volume rm $volume ; done
