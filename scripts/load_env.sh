#!/usr/bin/env bash

if [ -f ".env" ]; then
  set -a
  . .env
  set +a
fi
