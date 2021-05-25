FROM ubuntu:20.04
MAINTAINER Charlie Lewis <clewis@iqt.org>
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        bison \
        build-essential \
        ca-certificates \
        curl \
        flex \
        git \
        gnupg \
        iproute2 \
        iptables \
        iputils-ping \
        libbson-dev \
        libcurl4-gnutls-dev \
        libgcrypt-dev \
        libgnutls28-dev \
        libidn11-dev \
        libmicrohttpd-dev \
        libmongoc-dev \
        libnghttp2-dev \
        libsctp-dev \
        libssl-dev \
        libtins-dev \
        libyaml-dev \
        lksctp-tools \
        mongodb-clients \
        netbase \
        net-tools \
        ninja-build \
        pkg-config \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        tcpdump \
        tshark && \
    apt-get clean
RUN python3 -m pip install meson
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get -y install nodejs

RUN git clone https://github.com/anarkiwi/open5gs.git -b tap
WORKDIR /open5gs
RUN meson build && ninja -C build install
RUN ldconfig
WORKDIR /open5gs/webui
RUN npm install && npm run build
RUN ln -s /usr/local/lib/*/freeDiameter /freeDiameter

ENTRYPOINT ["/bin/sh"]
