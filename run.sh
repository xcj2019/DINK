#!/bin/sh

XSOCK=/tmp/.X11-unix
XAUTH=/home/ai8/.Xauthority
SHARED_DIR=/home/dink/shared_dir
HOST_DIR=/home/ai8/dink_dir

if [ "$1" = "kinetic" ] || [ "$1" = "indigo" ]
then
    echo "Use $1"
else
    echo "Select distribution, kinetic|indigo"
    exit
fi

if [ "$2" = "" ]
then
    # Create Shared Folder
    mkdir -p $HOST_DIR
else
    HOST_DIR=$2
fi
echo "Shared directory: ${HOST_DIR}"

sudo nvidia-docker run \
    -it --rm \
    --volume=$XSOCK:$XSOCK:rw \
    --volume=$XAUTH:$XAUTH:rw \
    --volume=$HOST_DIR:$SHARED_DIR:rw \
    --env="XAUTHORITY=${XAUTH}" \
    --env="DISPLAY=${DISPLAY}" \
    -u dink \
    --privileged -v /dev/bus/usb:/dev/bus/usb \
    --net=host \
registry.cn-hangzhou.aliyuncs.com/dink_190123/dink:0.1.1
