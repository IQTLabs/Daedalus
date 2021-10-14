#!/bin/bash
SS=$(ss -SOH state established)
if [[ "${SS}" == "" ]] ; then exit 1 ; fi
exit 0
