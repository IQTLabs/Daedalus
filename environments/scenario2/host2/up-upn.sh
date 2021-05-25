#!/bin/bash

SCENARIO=$1

cd dovesnap
MIRROR_BRIDGE_OUT=enp4s0 MIRROR_BRIDGE_IN=enp3s0 FAUCETCONFRPC_IP=192.168.199.1 STACK_OFCONTROLLERS=tcp:192.168.199.1:6653,tcp:192.168.199.1:6654 docker-compose -f docker-compose.yml up -d --build
cd ..

docker network create -o ovs.bridge.dpid=0x620 -o ovs.bridge.mode=flat --subnet 192.168.27.0/24 --gateway 192.168.27.1 --ipam-opt com.docker.network.bridge.name=upn -o ovs.bridge.add_ports=VLAN27/1 -o ovs.bridge.vlan=27 -o ovs.bridge.controller=tcp:192.168.199.1:6653,tcp:192.168.199.1:6654 -o ovs.bridge.mtu=9000 --ipam-opt com.docker.network.driver.mtu=9000 --internal -d ovs upn

docker network create -o ovs.bridge.dpid=0x630 -o ovs.bridge.mode=flat --subnet 192.168.28.0/24 --gateway 192.168.28.1 --ipam-opt com.docker.network.bridge.name=rfn -o ovs.bridge.add_ports=VLAN28/1 -o ovs.bridge.vlan=28 -o ovs.bridge.controller=tcp:192.168.199.1:6653,tcp:192.168.199.1:6654 -o ovs.bridge.mtu=9000 --ipam-opt com.docker.network.driver.mtu=9000 --internal -d ovs rfn

#docker network create -o ovs.bridge.dpid=0x630 -o ovs.bridge.mode=nat --subnet 192.168.28.0/24 --gateway 192.168.28.1 --ipam-opt com.docker.network.bridge.name=rfn -o ovs.bridge.nat_acl=protectrfn -o ovs.bridge.add_ports=VLAN28/1 -o ovs.bridge.vlan=28 -o ovs.bridge.controller=tcp:192.168.199.1:6653,tcp:192.168.199.1:6654 -o ovs.bridge.mtu=9000 --ipam-opt com.docker.network.driver.mtu=9000 --internal -d ovs rfn


cd srsLTE && docker build -t srslte . && cd ..
docker build -t open5gs .

docker-compose -f docker-compose-5g-nsa-upn.yml up -d --build

sudo nsenter -n -t $(docker inspect --format {{.State.Pid}} enb) ip route del default
sudo nsenter -n -t $(docker inspect --format {{.State.Pid}} enb) ip route add default via 192.168.27.1

for c in upf upf2 ; do
	        sudo nsenter -n -t $(docker inspect --format {{.State.Pid}} $c) sysctl -w net.ipv4.conf.all.send_redirects=0
		        sudo nsenter -n -t $(docker inspect --format {{.State.Pid}} $c) sysctl -w net.ipv4.conf.ogstap.send_redirects=0
		done
		sudo nsenter -n -t $(docker inspect --format {{.State.Pid}} upf2) sysctl -w net.ipv4.conf.ogstap2.send_redirects=0

