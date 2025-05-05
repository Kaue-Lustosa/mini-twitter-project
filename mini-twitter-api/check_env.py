#!/usr/bin/env python
import os
import sys

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        'DJANGO_SETTINGS_MODULE',
    ]
    
    optional_vars = [
        'napi_a1rr0z660zpwblab1a8xycroojcxxm2o8d3us3n439jamea84wit5sxvcfqlu054',
        'miniTwitterProject',
        'REACT_APP_API_URL',
    ]
    
    # Check required variables
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"ERROR: The following required environment variables are not set: {', '.join(missing_vars)}")
        return False
    
    # Print optional variables
    print("Environment variables:")
    for var in required_vars + optional_vars:
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if 'PASSWORD' in var or 'SECRET' in var or 'KEY' in var:
                value = '*' * 8
            print(f"  {var}: {value}")
        else:
            print(f"  {var}: Not set")
    
    return True

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mini_twitter.settings')
    
    if not check_environment():
        sys.exit(1)
    
    print("Environment check passed!")
