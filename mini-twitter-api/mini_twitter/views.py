from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import redirect, render
from django.http import JsonResponse
from .utils import get_mini_twitter_settings

@api_view(['GET'])
@permission_classes([AllowAny])
def app_settings(request):
    """
    Return application settings that are safe to expose to the frontend.
    """
    settings = get_mini_twitter_settings()
    
    # Filter out any sensitive information if needed
    safe_settings = {
        'project_name': 'Mini Twitter',
        'version': '1.0.0',
    }
    
    # Add any non-sensitive settings from the environment
    if 'theme' in settings:
        safe_settings['theme'] = settings['theme']
    
    if 'features' in settings:
        safe_settings['features'] = settings['features']
    
    return Response(safe_settings)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    Root view for the API.
    """
    return Response({
        'message': 'Welcome to Mini Twitter API',
        'documentation': request.build_absolute_uri('/swagger/'),
        'endpoints': {
            'users': request.build_absolute_uri('/api/users/'),
            'posts': request.build_absolute_uri('/api/posts/'),
            'settings': request.build_absolute_uri('/api/settings/'),
        }
    })

def root_redirect(request):
    """
    Render the welcome page for the root URL.
    """
    return render(request, 'index.html')