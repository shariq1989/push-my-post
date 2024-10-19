#!/bin/bash

echo "Rescanning sites"
cd ~/development/push-my-post || exit
docker-compose exec web python manage.py scan_sites >>~/log_files/cron_logs.log 2>&1
