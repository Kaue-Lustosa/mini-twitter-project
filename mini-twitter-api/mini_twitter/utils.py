import os
import json

def get_mini_twitter_settings():
    """
    Get the Mini Twitter Project settings from environment variables.
    Returns a dictionary of settings or an empty dictionary if not found.
    """
    mini_twitter_env = os.environ.get('miniTwitterProject')
    
    if mini_twitter_env:
        try:
            # Try to parse as JSON if it's a JSON string
            return json.loads(mini_twitter_env)
        except json.JSONDecodeError:
            # If it's not JSON, return as a string
            return {'value': mini_twitter_env}
    
    return {}