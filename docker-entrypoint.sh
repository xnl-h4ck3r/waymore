#!/bin/bash
set -e

# Function to create directories with proper permissions
create_output_dirs() {
    # Ensure base results directory exists with appuser ownership
    mkdir -p /app/results
    chown appuser:appuser /app/results
    
    # Parse arguments to find -oR value and create that directory if specified
    args=("$@")
    for i in "${!args[@]}"; do
        if [[ "${args[$i]}" == "-oR" ]] || [[ "${args[$i]}" == "--output-responses" ]]; then
            # Get the next argument which is the output directory
            if [ $((i+1)) -lt ${#args[@]} ]; then
                output_dir="${args[$((i+1))]}"
                # Remove leading slash if present
                output_dir="${output_dir#/}"
                # Create the directory if it doesn't exist
                if [ -n "$output_dir" ]; then
                    mkdir -p "/app/$output_dir"
                    chown -R appuser:appuser "/app/$output_dir"
                fi
            fi
            break
        fi
    done
}

# If running as root, create directories then switch to appuser
if [ "$(id -u)" = "0" ]; then
    create_output_dirs "$@"
    exec gosu appuser waymore "$@"
else
    # Already running as appuser, just execute waymore
    exec waymore "$@"
fi
