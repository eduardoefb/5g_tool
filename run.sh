#!/bin/bash

export DATABASE_NAME="db01"
export DATABASE_USER="mongoadmin"
export DATABASE_PASS="secret"
export MONGODB_EXTERNAL_IP="127.0.0.1"
export CONTAINER_NAME="mongodb"
export SUBSCRIBER_COLLECTION_NAME="subscriber"
export OTLP_ENDPOINT="10.2.1.32:4317"
source config-rc

podman stop --all
podman rm --all

podman network rm mongodb-network &>/dev/null
podman network create mongodb-network
podman run -d --network mongodb-network \
    -p ${MONGODB_EXTERNAL_IP}:27017:27017  \
    --name ${CONTAINER_NAME} \
    -e MONGO_INITDB_ROOT_USERNAME=${DATABASE_USER} \
    -e MONGO_INITDB_ROOT_PASSWORD=${DATABASE_PASS} \
    docker.io/library/mongo 

podman run -d \
  -e COLLECTOR_ZIPKIN_HOST_PORT=:9411 \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  -p 9411:9411 \
  docker.io/jaegertracing/all-in-one:latest

if [ ! -d env ]; then
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
fi
source env/bin/activate
hypercorn main:app --bind 0.0.0.0:9999 --workers 4    
