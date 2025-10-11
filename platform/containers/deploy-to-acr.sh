#!/usr/bin/env bash
set -euo pipefail
ACR=usfacr.azurecr.io
IMAGE=usf-deploy-runner:latest
docker build -t $ACR/$IMAGE .
echo "Push with: az acr login --name usfacr && docker push $ACR/$IMAGE"
