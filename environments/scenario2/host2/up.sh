#!/bin/bash

SCENARIO=$1
echo "vlan: $VLAN" > scenario-"$SCENARIO"-cpn.txt

cd dovesnap
MIRROR_BRIDGE_OUT=enp4s0 MIRROR_BRIDGE_IN=enp3s0 FAUCETCONFRPC_IP=192.168.199.1 STACK_OFCONTROLLERS=tcp:192.168.199.1:6653,tcp:192.168.199.1:6654 docker-compose -f docker-compose.yml up -d --build
cd ..

docker network create -o ovs.bridge.dpid=0x600 -o ovs.bridge.mode=nat --subnet 192.168.26.0/24 --gateway 192.168.26.1 --ipam-opt com.docker.network.bridge.name=cpn -o ovs.bridge.nat_acl=protectcpn -o ovs.bridge.add_ports=VLAN26/1 -o ovs.bridge.vlan=26 -o ovs.bridge.controller=tcp:192.168.199.1:6653,tcp:192.168.199.1:6654 -o ovs.bridge.add_copro_ports=enp2s0/999 -o ovs.bridge.mtu=9000 --ipam-opt com.docker.network.driver.mtu=9000 --internal -d ovs cpn

docker network create -o ovs.bridge.dpid=0x610 -o ovs.bridge.mode=flat -o ovs.bridge.add_ports=VLAN29/1 -o ovs.bridge.vlan=29 -o ovs.bridge.dhcp=true -o ovs.bridge.controller=tcp:192.168.199.1:6653,tcp:192.168.199.1:6654 -o ovs.bridge.add_copro_ports=enp2s0/999 --ipam-driver null --internal -d ovs desktops

cd mongoloader && docker build -t mongoloader . && cd ..

docker build -t open5gs . && docker-compose -f docker-compose-5g-nsa-cpn.yml up -d --build

docker-compose -f docker-compose-5g-nsa-cpn.yml -f docker-compose-5g-nsa-upn.yml logs -f
