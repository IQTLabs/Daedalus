#!/bin/bash

NRFSBI=192.168.26.61:7777
ALLREG="AMF AUSF BSF NSSF PCF SMF UDM UDR"

instances=$(curl -s -A "NRF" --http2-prior-knowledge "$NRFSBI"/nnrf-nfm/v1/nf-instances| jq -r "._links.items[].href")
registered=""
for instance in $instances ; do
    nfmeta=$(curl -s --http2-prior-knowledge "$instance" |jq -r ".nfType,.nfStatus")
    # Read nftype and nfstatus into an array (from space delimited string).
    # We can't use the (VAR) format to array-ize due to shellcheck, requirements for quoting.
    read -r -d " " -a nfmeta <<< "${nfmeta}"
    nftype=${nfmeta[0]}
    nfstatus=${nfmeta[1]}
    if [ "$nfstatus" != "REGISTERED" ] ; then
        # this service not registered
        continue
    fi
    if [[ "$ALLREG" != *"$nftype"* ]]; then
	# this service not required
	continue
    fi
    echo "${nftype}": "${nfstatus}"
    registered="${nftype}\n${registered}"
done
registered=$(echo -e "${registered}"|sort|xargs)

if [ "$registered" == "$ALLREG" ] ; then
    echo OK
    exit 0
fi

echo not all present: "${registered}" need "${ALLREG}"
exit 1
