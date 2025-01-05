#!/bin/bash

echo "Generating Pinterest Suggestions"

# Ensure the log directory exists
mkdir -p ~/log_files

# Navigate to the project directory
cd ~/development/push-my-post || exit

# Clear the log file
> ~/log_files/pin_suggestions_cron.log

# Run the management command and write logs
docker-compose exec web python manage.py pin_board_suggestions >> ~/log_files/pin_suggestions_cron.log 2>&1
