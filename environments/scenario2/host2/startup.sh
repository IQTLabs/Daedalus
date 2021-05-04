#!/bin/bash

sudo ip link add tpmirrorint type veth peer name tpmirror
sudo ip link set tpmirrorint up || exit 1
sudo ip link set tpmirror up || exit 1

TPFAUCETPREFIX=/tmp/tpfaucet
sudo rm -rf $TPFAUCETPREFIX && mkdir -p $TPFAUCETPREFIX/etc/faucet && cp config/*yaml $TPFAUCETPREFIX/etc/faucet || exit 1

git clone https://github.com/iqtlabs/dovesnap || echo "... ok."
cd dovesnap && git pull && MIRROR_BRIDGE_OUT=tpmirrorint FAUCET_PREFIX=$TPFAUCETPREFIX docker-compose -f docker-compose.yml -f docker-compose-standalone.yml up -d --build && cd .. || exit 1

DOVESNAPOPTS="-o ovs.bridge.controller=tcp:127.0.0.1:6653,tcp:127.0.0.1:6654 -o ovs.bridge.mtu=9000 --ipam-opt com.docker.network.driver.mtu=9000 --internal"
docker network create $DOVESNAPOPTS -o ovs.bridge.vlan=26 -o ovs.bridge.dpid=0x620 -o ovs.bridge.mode=nat --subnet 192.168.26.0/24 --gateway 192.168.26.1 --ipam-opt com.docker.network.bridge.name=cpn -o ovs.bridge.nat_acl=protectcpn -d ovs cpn || exit 1
docker network create $DOVESNAPOPTS -o ovs.bridge.vlan=27 -o ovs.bridge.dpid=0x630 -o ovs.bridge.mode=nat --subnet 192.168.27.0/24 --gateway 192.168.27.1 --ipam-opt com.docker.network.bridge.name=upn -o ovs.bridge.nat_acl=protectupn -d ovs upn || exit 1
docker network create $DOVESNAPOPTS -o ovs.bridge.vlan=28 -o ovs.bridge.dpid=0x640 -o ovs.bridge.mode=flat --subnet 192.168.28.0/24 --ipam-opt com.docker.network.bridge.name=rfn -o ovs.bridge.nat_acl=protectrfn -d ovs rfn || exit

cd srsLTE && docker build -t srslte . && cd ..
cd mongoloader && docker build -t mongoloader . && cd ..

docker build -t open5gs . && docker-compose -f docker-compose-5g-nsa-cpn.yml -f docker-compose-5g-nsa-upn.yml up -d --build

sudo nsenter -n -t $(docker inspect --format {{.State.Pid}} enb) ip route del default
sudo nsenter -n -t $(docker inspect --format {{.State.Pid}} enb) ip route add default via 192.168.27.1

for c in upf upf2 ; do
	sudo nsenter -n -t $(docker inspect --format {{.State.Pid}} $c) sysctl -w net.ipv4.conf.all.send_redirects=0
	sudo nsenter -n -t $(docker inspect --format {{.State.Pid}} $c) sysctl -w net.ipv4.conf.ogstun.send_redirects=0
done
sudo nsenter -n -t $(docker inspect --format {{.State.Pid}} upf2) sysctl -w net.ipv4.conf.ogstun2.send_redirects=0

docker-compose -f docker-compose-5g-nsa-cpn.yml -f docker-compose-5g-nsa-upn.yml logs -f
