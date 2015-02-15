#!/bin/bash 
##
## OTP-Generator
## =============
## (using the RPi's hardware RNG)
##
## By Nicolai Lang


## 0. Settings
##****************************

## Path to the RNG
RNG="/dev/hwrng"
## Pat where the pads will be stored
DIR="/home/nicolai/OneTimePads"
## Size of each pad in MiB (default: 1 GiB)
SIZE=1000 #100000
## Maximum number of pads
MAX=6
## Blockfile
BASE="$(dirname "$0")"
BLOCK="$BASE/otpgen.block"

## Colors
RD=$(tput setaf 1)
GR=$(tput setaf 2)
YE=$(tput setaf 3)
DEF=$(tput sgr0)

## 1. Generating OTPs
##************************

if [ ! -f $BLOCK ]
then

    touch $BLOCK

    printf "===================================================\n"
    printf "${GR}>> HARDWARE RANDOM NUMBER GENERATOR for RPi${DEF}\n"
    printf "===================================================\n"

    NAME="otp"
    SUFFIX="pad"
    REGEX="^${NAME}_.*\.${SUFFIX}$"

    ## Check number of pads present
    while [ "$(ls ${DIR} -b | grep ${REGEX} | wc -l)" -lt $MAX ]
    do

	DATE=`date +"%d-%m-%Y_%H-%M-%S"` 
	FULLNAME="${NAME}_${DATE}.${SUFFIX}"
	OPTIONS="bs=1024 count=$(($SIZE*1024))"

	printf ">> ${RD}$(ls ${DIR} -b | grep ${REGEX} | wc -l) of ${MAX} ${SIZE} MB-pads present.${DEF}\n"
	printf ">> Generating OTP '${YE}${FULLNAME}${DEF}' ... \n"

	dd $OPTIONS if=$RNG of="${DIR}/${FULLNAME}"

	printf "[done]\n"
	printf "===================================================\n"

	sleep 1

    done

    printf "${GR}>> Nothing to do anymore. Exiting ...${DEF}\n"
    printf "===================================================\n"

    rm $BLOCK

fi

exit 0
