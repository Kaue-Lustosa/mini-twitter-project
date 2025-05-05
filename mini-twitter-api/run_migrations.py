#!/usr/bin/env python
import os
import django
import sys

def run_migrations():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mini_twitter.settings')
    django.setup()
    
    # Import Django's management module
    from django.core.management import call_command
    
    try:
        # Make migrations
        print("Creating migrations...")
        call_command('makemigrations', 'users', 'posts')
        
        # Apply migrations
        print("Applying migrations...")
        call_command('migrate')
        
        print("Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"Error during migrations: {e}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    if not success:
        sys.exit(1)