#!/bin/bash

# Ensure the log directory exists
mkdir -p ~/log_files

# Clear (or create) the log file
> ~/log_files/site_scan_cron.log

echo "Rescanning sites"

# Navigate to the project directory
cd ~/development/push-my-post || exit

# Run the management command and write logs
docker-compose exec web python manage.py scan_sites >> ~/log_files/site_scan_cron.log 2>&1