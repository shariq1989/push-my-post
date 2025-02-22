#!/bin/bash

echo "Entering project dir"
# Navigate to your project directory
cd /root/development/push-my-post/

echo "Pulling updates from repo"
# Pull the latest changes from the Git repository
git pull

echo "Shutting down containers"
# Stop and remove Docker containers
docker-compose down --remove-orphans

echo "Bringing containers back up"
# Build and start Docker containers using the production configuration
sudo docker-compose -f docker-compose-prod.yml up --build -d

echo "Running migrations"
sudo docker-compose exec web python manage.py migrate

echo "Updating static files"
# Collect static files
sudo docker-compose exec web python manage.py collectstatic --noinput

echo "Tailing application log"
# Tail log
sudo docker logs --follow push-my-post_web_1
