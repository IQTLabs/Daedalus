FROM ubuntu:20.04
LABEL maintainers="Charlie Lewis <clewis@iqt.org>"
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
        openvswitch-switch \
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

RUN git clone https://github.com/open5gs/open5gs.git -b v2.3.2
WORKDIR /open5gs
RUN meson build && ninja -C build install
RUN ln -s /usr/local/lib/*/freeDiameter /freeDiameter
RUN ldconfig
WORKDIR /open5gs/webui
RUN npm install && npm run build
RUN mkdir -p /usr/local/var/log/open5gs
WORKDIR /usr/local/var/log/open5gs
RUN touch smf.log

COPY scripts /scripts

WORKDIR /open5gs
# TODO: provide certs externally; open5gs will use locally built certs for now via make_certs.sh in this image.
RUN sed -r -i 's/C=\w+/C=NZ/g;s/ST=\w+/ST=UpperHutt/g;s/L=\w+/L=Wellington/g' misc/make_certs.sh && \
  mkdir /certs && misc/make_certs.sh /certs
