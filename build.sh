#!/usr/bin/env bash
# exit on error
set -o errexit

# Install build dependencies
apt-get update && apt-get install -y libpq-dev pkg-config

# Set environment variable to avoid Rust build for asyncpg
export ASYNCPG_NO_RUST=1

# Install Python dependencies
pip install -r requirements.txt 