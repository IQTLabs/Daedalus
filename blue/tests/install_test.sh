#!/bin/sh

export DEBIAN_FRONTEND=noninteractive && \
  echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections
  sudo apt-get update && \
  sudo apt-get remove docker docker-engine docker.io containerd runc && \
  sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common && \
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - && \
  sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
  sudo apt-get update && sudo apt-get install docker-ce docker-ce-cli containerd.io python3-setuptools python3-dev uhd-host && \
  sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
  sudo chmod +x /usr/local/bin/docker-compose && \
  sudo pip3 install -r blue/requirements.txt && \
  sudo pip3 install -r blue/generate_fs/requirements.txt && \
  sudo pip3 install -r blue/nfsconfuser/confused/requirements.txt && \
  sudo pip3 install -r blue/tests/requirements.txt
