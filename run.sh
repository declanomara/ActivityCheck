#!/bin/bash

# Define the maximum number of retries
max_retries=5

# Define the initial delay in seconds
initial_delay=1

# Define the exponential factor
exponential_factor=2

# Define the command to run main.py
command="python3 main.py"

# Initialize the retry count
retry_count=0

# Run the command with exponential backoff
while true; do
    # Run the command
    $command
    
    # Check the exit status
    exit_status=$?
    
    # If the command succeeded, break out of the loop
    if [ $exit_status -eq 0 ]; then
        break
    fi
    
    # Increment the retry count
    retry_count=$((retry_count + 1))
    
    # If the maximum number of retries has been reached, exit with an error
    if [ $retry_count -eq $max_retries ]; then
        echo "Error: Maximum number of retries reached"
        exit 1
    fi
    
    # Calculate the delay for the next retry
    delay=$((initial_delay * exponential_factor ** retry_count))
    
    # Sleep for the calculated delay
    sleep $delay
done