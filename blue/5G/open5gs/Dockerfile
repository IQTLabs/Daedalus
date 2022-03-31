FROM ubuntu:20.04 AS builder
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        bison \
        build-essential \
        ca-certificates \
        flex \
        git \
        gnupg \
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
        libtalloc-dev \
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
        python3-wheel && \
    apt-get clean
# TODO: need to pin meson to workaround "Target "../dict_dcca_3gpp" has a path segment pointing to directory "subprojects/freeDiameter/extensions/dict_dcca_3gpp/..". This is an error."
RUN python3 -m pip install -U meson==0.59.3
RUN apt-get install -y --no-install-recommends npm nodejs

RUN git clone https://github.com/open5gs/open5gs.git -b v2.4.3
WORKDIR /open5gs
RUN meson build && ninja -C build install
WORKDIR /open5gs/webui
RUN npm install && npm run build
WORKDIR /open5gs
# TODO: provide certs externally; open5gs will use locally built certs for now via make_certs.sh in this image.
RUN sed -r -i 's/C=\w+/C=NZ/g;s/ST=\w+/ST=UpperHutt/g;s/L=\w+/L=Wellington/g' misc/make_certs.sh && \
  mkdir /certs && misc/make_certs.sh /certs

FROM ubuntu:20.04
LABEL maintainers="Charlie Lewis <clewis@iqt.org>"
ENV DEBIAN_FRONTEND noninteractive
COPY --from=builder /usr/local/lib/*-linux-gnu /usr/local/lib/
COPY --from=builder /usr/lib/*-linux-gnu /usr/lib/
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        jq \
        iproute2 \
        iptables \
        iputils-ping \
        lksctp-tools \
        net-tools \
        openvswitch-switch \
        tcpdump \
        tshark && \
    apt-get clean
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get install -y --no-install-recommends npm nodejs
COPY --from=builder /certs /certs
COPY --from=builder /usr/local/bin/open5gs* /usr/local/bin/
COPY --from=builder /open5gs/webui /webui
COPY --from=builder /usr/local/lib/*/freeDiameter /freeDiameter
COPY --from=builder /usr/lib/libtins* /usr/lib/
COPY scripts /scripts
RUN mkdir -p /usr/local/var/log/open5gs
WORKDIR /usr/local/var/log/open5gs
RUN touch smf.log
