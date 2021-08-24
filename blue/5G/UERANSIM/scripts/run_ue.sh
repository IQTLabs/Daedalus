#!/bin/sh

/scripts/add_default_route.sh &
exec /UERANSIM/build/nr-ue "$*"
