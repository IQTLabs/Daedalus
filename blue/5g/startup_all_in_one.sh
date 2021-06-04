#!/bin/bash

cd srsLTE
docker build -t srslte .
cd ..

docker build -t open5gs .
docker-compose -f docker-compose-5g-nsa.yml up -d --build
docker-compose -f docker-compose-5g-nsa.yml logs -f
