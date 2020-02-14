#!/usr/bin/env sh

kubectl port-forward --namespace kr-dev-01 svc/default-broker 8000:80