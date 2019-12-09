#!/usr/bin/env bash

if    ls -1qA ./apify_storage | grep -q .
then  exit 0
else  echo "output directory is empty!"; exit 1
fi
