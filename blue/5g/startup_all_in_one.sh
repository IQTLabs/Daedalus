#!/bin/bash

cd srsRAN
docker build -t srsran .
cd ..

docker build -t open5gs .
docker-compose -f docker-compose-5g-nsa.yml up -d --build
docker-compose -f docker-compose-5g-nsa.yml logs -f
