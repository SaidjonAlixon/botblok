#!/usr/bin/env bash
# exit on error
set -o errexit

# Install build dependencies
apt-get update && apt-get install -y libpq-dev pkg-config

# Install asyncpg separately with special flags
pip install --no-cache-dir --only-binary=:all: asyncpg

# Install other Python dependencies
pip install -r requirements.txt 