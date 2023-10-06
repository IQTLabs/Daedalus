FROM ubuntu:22.04 AS builder
ENV DEBIAN_FRONTEND noninteractive
# hadolint ignore=DL3008
RUN apt-get update && \
    apt install -y ca-certificates curl gnupg
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
# hadolint ignore=DL3008
RUN apt-get install -y --no-install-recommends \
        bison \
        build-essential \
        ca-certificates \
        cmake \
        flex \
        git \
        gnupg \
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
        meson \
        net-tools \
        netbase \
        ninja-build \
        nodejs \
        npm \
        pkg-config \
        python3-pip \
        python3-setuptools \
        python3-wheel

RUN git clone https://github.com/open5gs/open5gs.git -b v2.6.6
WORKDIR /open5gs
RUN meson build && ninja -C build install
WORKDIR /open5gs/webui
RUN npm install && npm run build
WORKDIR /open5gs
# TODO: provide certs externally; open5gs will use locally built certs for now via make-certs.sh in this image.
RUN sed -r -i 's/C=\w+/C=NZ/g;s/ST=\w+/ST=UpperHutt/g;s/L=\w+/L=Wellington/g' misc/make-certs.sh && \
  mkdir /certs && misc/make-certs.sh /certs

FROM ubuntu:22.04
LABEL maintainers="Charlie Lewis <clewis@iqt.org>"
ENV DEBIAN_FRONTEND noninteractive
COPY --from=builder /etc/apt/keyrings/nodesource.gpg /etc/apt/keyrings/nodesource.gpg
COPY --from=builder /etc/apt/sources.list.d/nodesource.list /etc/apt/sources.list.d/nodesource.list
COPY --from=builder /usr/local /usr/local
COPY --from=builder /certs /certs
COPY --from=builder /open5gs/webui /webui
RUN ln -s /usr/local/lib/*/freeDiameter /freeDiameter
WORKDIR /usr/local/var/log/open5gs
RUN touch smf.log
COPY scripts /scripts
# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        iproute2 \
        iptables \
        iputils-ping \
        jq \
        libbson-1.0-0 \
        libcurl3-gnutls \
        libidn12 \
        libmicrohttpd12 \
        libmongoc-1.0-0 \
        libtalloc2 \
        libtins4.0 \
        libyaml-0.2 \
        lksctp-tools \
        nodejs \
        npm \
        net-tools \
        openvswitch-switch \
        tcpdump \
        tshark && \
    apt-get clean
