#!/bin/bash

# Check if project name is provided
if [ $# -eq 0 ]; then
    echo "Please provide a project name."
    echo "Usage: $0 <project_name>"
    exit 1
fi

# Set variables
PROJECT_NAME=$1
TEMPLATE_PATH="$HOME/Documents/Development/shariq1989-django-starter"  # Update this path

# Create new project directory
echo "Creating new project directory: $PROJECT_NAME"
mkdir "$PROJECT_NAME"
cd "$PROJECT_NAME" || exit

# Copy template contents using rsync to avoid copying . and ..
echo "Copying template contents..."
rsync -a --exclude=".git" "$TEMPLATE_PATH"/ .   # Exclude .git if necessary

# Initialize new Git repository
echo "Initializing new Git repository..."
git init

echo "Project $PROJECT_NAME has been created successfully!"
echo "Don't forget to update project-specific files and environment variables."