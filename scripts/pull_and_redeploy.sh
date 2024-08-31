#!/bin/bash

echo "Entering recipe_research dir"
# Navigate to your project directory
cd ~/Development/recipe_research/

echo "Pulling updates from repo"
# Pull the latest changes from the Git repository
git pull

echo "Shutting down containers"
# Stop and remove Docker containers
sudo docker-compose down

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
sudo docker logs --follow recipe_research_web_1