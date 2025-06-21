#!/usr/bin/env bash
# exit on error
set -o errexit

# Install build dependencies
apt-get update && apt-get install -y libpq-dev pkg-config

# Install Python dependencies, forcing non-rust build for asyncpg
ASYNCPG_NO_RUST=1 pip install -r requirements.txt 