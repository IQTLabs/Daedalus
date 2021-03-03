# TODO: alpine apparently doesn't have ganesha
FROM debian:stable

RUN apt-get update && apt-get install -y --no-install-recommends netbase python3-pip python3-dev python3-setuptools python3-wheel git libfuse-dev
RUN apt-get update && apt-get install -y --no-install-recommends nfs-ganesha nfs-ganesha-vfs
RUN git clone https://github.com/anarkiwi/confused && cd confused && pip3 install -r requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends procps net-tools tcpdump strace
RUN mkdir -p /real /fake /share && rm -f /etc/ganesha/*
COPY serve.sh /serve.sh
COPY ganesha.conf /etc/ganesha
ENTRYPOINT ["/serve.sh"]

# docker build -f Dockerfile . -t nfsconfuser && docker run --device /dev/fuse --cap-add SYS_ADMIN --cap-add DAC_READ_SEARCH --security-opt apparmor:unconfined -p 0.0.0.0:2049:2049 -v /fake:/fake -v /real:/real -ti nfsconfuser
