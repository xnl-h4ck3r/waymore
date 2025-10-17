#!/bin/bash
set -e

# Create results directory if it doesn't exist and ensure proper permissions
if [ ! -d "/app/results" ]; then
    mkdir -p /app/results
fi

# Execute waymore with all passed arguments
exec waymore "$@"
