#!/bin/bash

# Install required packages first
pip install -r requirements.txt

# Check environment variables
echo "Checking environment variables..."
python check_env.py
if [ $? -ne 0 ]; then
  echo "Environment check failed. Exiting."
  exit 1
fi

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "Redis started"

# Run migrations first
echo "Running migrations..."
python manage.py makemigrations users posts
python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mini_twitter.settings')
django.setup()
from django.contrib.auth.models import User
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')
        print('Superuser created')
    else:
        print('Superuser already exists')
except Exception as e:
    print(f'Error creating superuser: {e}')
"

# Start the application
echo "Starting application..."
exec "$@"