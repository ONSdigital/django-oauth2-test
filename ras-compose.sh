#!/bin/bash

build () {
 # build image, uses this to gain network access to perform the migrate operation during the build process
 docker build . -t oauth2-service --network=rasdockerdev_default
}

start() {
 # start the oauth server connecting to the external network
 docker run --network=rasdockerdev_default -d --name=oauth2-service oauth2-service
}

stop () {
 docker stop oauth2-service
}

remove() {
docker rm oauth2-service
docker rmi oauth2-service
}


usage() {
echo "use flags:- up: build and run oauth2-service , run: run prebuilt oauth2-service, stop: stop oauth2-service,  down: stop oauth2-service and remove image"
}

case "$1" in 
 up)
  build
  start 
  ;;
 run)
  docker restart oauth2-service
  ;;
 stop)
  stop
  ;;
 down)
  stop 
  remove
  ;;
 *)
  usage
  ;;
esac
