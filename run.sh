#!/bin/bash

export DATABASE_NAME="db01"
export DATABASE_USER="mongoadmin"
export DATABASE_PASS="secret"
export MONGODB_EXTERNAL_IP="127.0.0.1"
export CONTAINER_NAME="mongodb"
export SUBSCRIBER_COLLECTION_NAME="subscriber"

source config-rc

podman stop mongodb &>/dev/null
podman rm mongodb &>/dev/null
podman network rm mongodb-network &>/dev/null
podman network create mongodb-network
podman run -d --network mongodb-network \
    -p ${MONGODB_EXTERNAL_IP}:27017:27017  \
    --name ${CONTAINER_NAME} \
    -e MONGO_INITDB_ROOT_USERNAME=${DATABASE_USER} \
    -e MONGO_INITDB_ROOT_PASSWORD=${DATABASE_PASS} \
    docker.io/library/mongo


python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
hypercorn main:app --bind 0.0.0.0:9999 --workers 4    
