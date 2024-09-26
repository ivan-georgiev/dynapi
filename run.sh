#!/bin/bash

IMAGE_NAME="ivangeorgievbg/dynapi"

version=$1
[[ -z "$version" ]] && version="$(date +%s)"

docker run  --name dynapi --rm -p 8080:8080 -e DYNAPP_VERSION=$version $IMAGE_NAME:latest
