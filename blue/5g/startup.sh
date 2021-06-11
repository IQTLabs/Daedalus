#!/bin/bash

BLADERF=0
ETTUS=0
LIMESDR=0
VUE=1
SRS_VERSION="release_21_04"

# -b: run bladeRF enb
# -e: run ettus enb
# -l: run limesdr enb
# -V: DO NOT run virtual enb and UEs.
# e.g., to run bladeRF only, ./startup.sh -bV

while getopts "belV" o; do
    case "${o}" in
        b)
            BLADERF=1
            ;;
        e)
            ETTUS=1
            ;;
        l)
            LIMESDR=1
            ;;
        V)
            VUE=0
            ;;
    esac
done
shift $((OPTIND-1))

echo start bladeRF: $BLADERF
echo start ettus: $ETTUS
echo start limesdr: $LIMESDR
echo start virtual UEs/eNB: $VUE

if [[ "$LIMESDR" -eq 1 ]]; then
	SRS_VERSION="release_19_12"
fi

echo building srsRAN version: $SRS_VERSION

cd srsRAN && docker build -f Dockerfile.base -t srsran:base . && docker build --build-arg SRS_VERSION="$SRS_VERSION" -f Dockerfile.srs -t srsran . && cd .. || exit 1
cd open5gs && docker build -t open5gs . && cd .. || exit 1

sudo ip link add tpmirrorint type veth peer name tpmirror
sudo ip link set tpmirrorint up || exit 1
sudo ip link set tpmirror up || exit 1

TPFAUCETPREFIX=/tmp/tpfaucet
sudo rm -rf $TPFAUCETPREFIX && mkdir -p $TPFAUCETPREFIX/etc/faucet && cp config/*yaml $TPFAUCETPREFIX/etc/faucet || exit 1

git clone https://github.com/iqtlabs/dovesnap || echo "... ok."
cd dovesnap && git pull && MIRROR_BRIDGE_OUT=tpmirrorint FAUCET_PREFIX=$TPFAUCETPREFIX docker-compose -f docker-compose.yml -f docker-compose-standalone.yml up -d --build && cd .. || exit 1

DOVESNAPOPTS="-o ovs.bridge.controller=tcp:127.0.0.1:6653,tcp:127.0.0.1:6654 -o ovs.bridge.mtu=9000 --ipam-opt com.docker.network.driver.mtu=9000 --internal"
docker network create $DOVESNAPOPTS -o ovs.bridge.vlan=26 -o ovs.bridge.dpid=0x620 -o ovs.bridge.mode=nat --subnet 192.168.26.0/24 --gateway 192.168.26.1 --ipam-opt com.docker.network.bridge.name=cpn -o ovs.bridge.nat_acl=protectcpn -d ovs cpn || exit 1
UPNIP=192.168.27
docker network create $DOVESNAPOPTS -o ovs.bridge.vlan=27 -o ovs.bridge.dpid=0x630 -o ovs.bridge.mode=nat --subnet ${UPNIP}.0/24 --gateway ${UPNIP}.1 --ipam-opt com.docker.network.bridge.name=upn -o ovs.bridge.nat_acl=protectupn -d ovs upn || exit 1

DOCKERFILES="-f docker-compose-5g-nsa-cpn.yml -f docker-compose-5g-nsa-upn.yml"

if [[ "$BLADERF" -eq 1 ]] ; then
        DOCKERFILES="$DOCKERFILES -f docker-compose-5g-nsa-upn-bladerf-enb.yml"
fi

if [[ "$ETTUS" -eq 1 ]] ; then
        uhd_find_devices
        DOCKERFILES="$DOCKERFILES -f docker-compose-5g-nsa-upn-ettus-enb.yml"
fi

if [[ "$LIMESDR" -eq 1 ]] ; then
        DOCKERFILES="$DOCKERFILES -f docker-compose-5g-nsa-upn-limesdr-enb.yml"
fi

if [[ "$VUE" -eq 1 ]] ; then
        docker network create $DOVESNAPOPTS -o ovs.bridge.vlan=28 -o ovs.bridge.dpid=0x640 -o ovs.bridge.mode=flat --subnet 192.168.28.0/24 --ipam-opt com.docker.network.bridge.name=rfn -o ovs.bridge.nat_acl=protectrfn -d ovs rfn || exit
        DOCKERFILES="$DOCKERFILES -f docker-compose-5g-nsa-upn-enb.yml -f docker-compose-5g-nsa-rfn-ue.yml"
fi

docker-compose $DOCKERFILES up -d --build || exit 1

if [[ "$VUE" -eq 1 ]] ; then
        sudo nsenter -n -t $(docker inspect --format {{.State.Pid}} enb) ip route del default || exit 1
        sudo nsenter -n -t $(docker inspect --format {{.State.Pid}} enb) ip route add default via ${UPNIP}.1 || exit 1
fi

docker-compose $DOCKERFILES logs -f
