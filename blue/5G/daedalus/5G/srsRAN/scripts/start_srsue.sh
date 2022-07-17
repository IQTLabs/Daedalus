#!/bin/sh

/scripts/add_default_route.sh &
exec srsue "$@"
