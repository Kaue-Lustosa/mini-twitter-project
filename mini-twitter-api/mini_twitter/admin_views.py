from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
import os

@staff_member_required
def environment_variables(request):
    """
    View to display environment variables (only accessible to staff/superusers).
    """
    # Filter environment variables to only show those related to the project
    env_vars = {
        key: value for key, value in os.environ.items()
        if key.startswith('MINI_') or 
           key.startswith('REACT_') or 
           key == 'miniTwitterProject'
    }
    
    return JsonResponse(env_vars)