#!/bin/sh

export DEBIAN_FRONTEND=noninteractive && \
  echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections && \
  sudo apt-get update && \
  sudo apt-get purge docker docker-engine docker.io containerd runc python3-yaml && \
  sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common && \
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - && \
  sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
  sudo apt-get update && sudo apt-get install docker-ce docker-ce-cli containerd.io && \
  sudo apt-get install nftables && sudo nft flush ruleset && sudo apt-get purge nftables && sudo apt-get --reinstall install iptables && \
  sudo update-alternatives --set iptables /usr/sbin/iptables-legacy && \
  sudo /etc/init.d/docker restart && \
  sudo apt-get update && sudo apt-get install python3-setuptools python3-dev uhd-host && \
  sudo python3 -m pip install -U pip && \
  sudo python3 -m pip install "./blue[generate_fs,confuser,test]"
