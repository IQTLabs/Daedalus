#!/bin/bash

docker ps -a

for i in $(docker ps -aq) ; do
  docker ps -a -f id="$i"
  docker logs "$i"
done
exit 1
