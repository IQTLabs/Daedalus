#!/bin/sh

/scripts/add_default_route.sh &
exec /usr/local/bin/nr-ue "$@"
