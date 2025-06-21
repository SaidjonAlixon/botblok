#!/usr/bin/env bash
# exit on error
set -o errexit

# Install build dependencies
apt-get update && apt-get install -y libpq-dev pkg-config

# Install Python dependencies
pip install -r requirements.txt 