#!/bin/sh

/root/add_default_route.sh &
exec srsue $*
