FROM ubuntu:22.04 as builder
LABEL maintainer="Charlie Lewis <clewis@iqt.org>"
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install --no-install-recommends -yq \
     build-essential \
     ca-certificates \
     cmake \
     git \
     g++ \
     libsctp-dev \
     make

WORKDIR /src
RUN git clone https://github.com/aligungr/UERANSIM -b v3.2.6
WORKDIR /src/UERANSIM
RUN make -j "$(nproc)"
WORKDIR /usr/local/bin
RUN cp /src/UERANSIM/build/* .

FROM ubuntu:22.04
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install --no-install-recommends -yq \
     ca-certificates \
     iproute2 \
     libsctp1 \
     lksctp-tools \
     tcpdump \
     iputils-ping \
     wget
COPY --from=builder /usr/local /usr/local
COPY scripts /scripts
RUN ldd /usr/local/bin/nr-gnb
RUN ldd /usr/local/bin/nr-ue
ENTRYPOINT ["/bin/sh"]
