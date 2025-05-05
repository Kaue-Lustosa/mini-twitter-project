from django.urls import path
from .admin_views import environment_variables

urlpatterns = [
    path('env-vars/', environment_variables, name='environment-variables'),
]
