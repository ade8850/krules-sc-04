#!/usr/bin/env sh

kubectl port-forward --namespace kr-dev-01 svc/ws-server 5678:80
