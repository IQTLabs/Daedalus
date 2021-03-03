#!/bin/bash
/sbin/rpcbind
/sbin/rpc.statd --no-notify
python3 /confused/confused.py /real /share /fake &
echo checking /share has content
while [[ "$(ls /share)" == "" ]] ; do
	echo waiting for /share
	sleep 1
done
echo starting ganesha
strace -f -o /var/log/ganesha/strace.log /usr/bin/ganesha.nfsd -F -L /var/log/ganesha/ganesha.log -N NIV_DEBUG
