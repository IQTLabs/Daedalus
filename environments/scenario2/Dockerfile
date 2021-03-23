FROM ubuntu:20.04
MAINTAINER Charlie Lewis <clewis@iqt.org>
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libmicrohttpd-dev \
        libnghttp2-dev \
        libcurl4-gnutls-dev \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        ninja-build \
        build-essential \
        flex \
        bison \
        git \
        libsctp-dev \
        libgnutls28-dev \
        libgcrypt-dev \
        libssl-dev \
        libidn11-dev \
        libmongoc-dev \
        libbson-dev \
        libyaml-dev \
        iproute2 \
        ca-certificates \
        netbase \
        tshark \
        iptables \
        net-tools \
        mongodb-clients \
        curl \
        gnupg \
        pkg-config \
        tcpdump \
        iputils-ping \
        lksctp-tools && \
    apt-get clean
RUN python3 -m pip install meson
RUN git clone https://github.com/open5gs/open5gs.git -b v2.1.7
WORKDIR /open5gs
COPY open5gs-freedia.txt .
RUN patch -p1 < open5gs-freedia.txt
RUN meson build && ninja -C build install
WORKDIR /

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN apt-get -y install nodejs

RUN cd /open5gs/webui && npm install && npm run build

ENTRYPOINT ["/bin/sh"]
