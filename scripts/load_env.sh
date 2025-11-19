#!/usr/bin/env bash

# Load environment variables from .env file if present

if [ -f ".env" ]; then
  set -a
  . .env
  set +a
fi
