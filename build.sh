#!/bin/bash

LABEL org.opencontainers.image.source=https://github.com/ivan-georgiev/dynapi
LABEL org.opencontainers.image.description="Dynapi configurable API"
LABEL org.opencontainers.image.licenses=MIT

IMAGE_NAME="ivangeorgievbg/dynapi"
IMAGE_NAME_GH="ghcr.io/ivangeorgiev/dynapi"

VERSION=$(cat version.txt)

echo "INFO: Building [$IMAGE_NAME:$VERSION]"

docker build \
-t "$IMAGE_NAME:$VERSION" \
-t "$IMAGE_NAME:latest" \
. || exit 1

[[ "$@" == *"push"* ]]  && echo "INFO: Push" \
&& docker push $IMAGE_NAME:$VERSION \
&& docker push $IMAGE_NAME:latest \
&& echo "INFO: Push completed"

[[ "$@" == *"run"* ]]  && echo "INFO: Run" && docker run --rm -p 8080:8080 \
    -e DYNAPP_VERSION="$VERSION" \
    -e DYNAPP_NOSIGNALS="true" \
    --name dynapi \
    $IMAGE_NAME:$VERSION
