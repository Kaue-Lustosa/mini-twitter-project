from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, LikeViewSet, RetweetViewSet

router = DefaultRouter()
router.register(r'', PostViewSet)

likes_router = DefaultRouter()
likes_router.register(r'', LikeViewSet)

retweets_router = DefaultRouter()
retweets_router.register(r'', RetweetViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('likes/', include(likes_router.urls)),
    path('retweets/', include(retweets_router.urls)),
]