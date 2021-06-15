#!/bin/bash

BLADERF=0
BLADERF_EARFCN=2700
ETTUS=0
ETTUS_EARFCN=1800
LIMESDR=0
LIMESDR_EARFCN=900
VUE=1
SRS_VERSION="release_21_04"
ENB=0
CPN=1
UPN=1

# -b: run bladeRF enb
# -B <n>: bladeRF EARFCN
# -e: run ettus enb
# -E <n>: ettus EARFCN
# -l: run limesdr enb
# -L <n>: limesdr EARFCN
# -V: DO NOT run virtual enb and UEs.
# -C: DO NOT run the CPN
# -U: DO NOT run the UPN
# e.g., to run bladeRF only, ./startup.sh -bV


while getopts "bB:eE:lL:VCU" o; do
    case "${o}" in
        b)
            BLADERF=1
            ENB=1
            ;;
        B)
            BLADERF_EARFCN=${OPTARG}
            ;;
        e)
            ETTUS=1
            ENB=1
            ;;
        E)
            ETTUS_EARFCN=${OPTARG}
            ;;
        l)
            LIMESDR=1
            ENB=1
            ;;
        L)
            LIMESDR_EARFCN=${OPTARG}
            ;;
        V)
            VUE=0
	    ;;
	C)
	    CPN=0
            ;;
	U)
	    UPN=0
            ;;
    esac
done
shift $((OPTIND-1))

if [[ "$VUE" -eq 1 ]] ; then ENB=1 ; fi

echo start bladeRF: $BLADERF
echo start ettus: $ETTUS
echo start limesdr: $LIMESDR
echo start virtual UEs/eNB: $VUE
echo start CPN: $CPN
echo start UPN: $UPN
echo start ENB: $ENB

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
DOCKERFILES=""

if [[ "$CPN" -eq 1 ]] ; then
        docker network create $DOVESNAPOPTS -o ovs.bridge.vlan=26 -o ovs.bridge.dpid=0x620 -o ovs.bridge.mode=routed --subnet 192.168.26.0/24 --gateway 192.168.26.1 --ipam-opt com.docker.network.bridge.name=cpn -o ovs.bridge.nat_acl=protectcpn -d ovs cpn || exit 1
        DOCKERFILES="$DOCKERFILES -f docker-compose-5g-nsa-cpn.yml"
fi

if [[ "$UPN" -eq 1 ]] ; then
        docker network create $DOVESNAPOPTS -o ovs.bridge.vlan=27 -o ovs.bridge.dpid=0x630 -o ovs.bridge.mode=nat --subnet 192.168.27.0/24 --gateway 192.168.27.1 --ipam-opt com.docker.network.bridge.name=upn -d ovs upn || exit 1
        DOCKERFILES="$DOCKERFILES -f docker-compose-5g-nsa-upn.yml"
fi

if [[ "$VUE" -eq 1 ]] ; then
        docker network create $DOVESNAPOPTS -o ovs.bridge.vlan=28 -o ovs.bridge.dpid=0x640 -o ovs.bridge.mode=flat --subnet 192.168.28.0/24 --ipam-opt com.docker.network.bridge.name=rfn -o ovs.bridge.nat_acl=protectrfn -d ovs rfn || exit
        DOCKERFILES="$DOCKERFILES -f docker-compose-5g-nsa-enb.yml -f docker-compose-5g-nsa-rfn-ue.yml"
fi

if [[ "$ENB" -eq 1 ]] ; then
        docker network create $DOVESNAPOPTS -o ovs.bridge.vlan=29 -o ovs.bridge.dpid=0x650 -o ovs.bridge.mode=routed --subnet 192.168.29.0/24 --gateway 192.168.29.1 --ipam-opt com.docker.network.bridge.name=upn -o ovs.bridge.nat_acl=protectenb -d ovs enb || exit 1
fi

if [[ "$BLADERF" -eq 1 ]] ; then
        export BLADERF_EARFCN
        DOCKERFILES="$DOCKERFILES -f docker-compose-5g-nsa-bladerf-enb.yml"
fi

if [[ "$ETTUS" -eq 1 ]] ; then
        export ETTUS_EARFCN
        uhd_find_devices
        DOCKERFILES="$DOCKERFILES -f docker-compose-5g-nsa-ettus-enb.yml"
fi

if [[ "$LIMESDR" -eq 1 ]] ; then
        export LIMESDR_EARFCN
        DOCKERFILES="$DOCKERFILES -f docker-compose-5g-nsa-limesdr-enb.yml"
fi

docker-compose $DOCKERFILES up -d --build || exit 1

if [[ "$VUE" -eq 1 ]] ; then
        sudo nsenter -n -t $(docker inspect --format {{.State.Pid}} enb) ip route del default || exit 1
        sudo nsenter -n -t $(docker inspect --format {{.State.Pid}} enb) ip route add default via 192.168.29.1 || exit 1
fi

docker-compose $DOCKERFILES logs -f
