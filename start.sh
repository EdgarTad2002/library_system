#!/bin/bash

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Load initial data from fixture
# Check if the initial_data.json exists before attempting to load
if [ -f initial_data.json ]; then
    echo "Loading initial data..."
    python manage.py loaddata initial_data.json
else
    echo "initial_data.json not found, skipping data load."
fi

# Start the Django development server
echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000
