from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
from jwt import decode as jwt_decode
from jwt import InvalidTokenError
from django.conf import settings

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Get the token from the query string
        query_string = scope.get('query_string', b'').decode()
        query_params = dict(param.split('=') for param in query_string.split('&') if param)
        
        token = query_params.get('token', None)
        
        # If no token, check headers
        if not token:
            headers = dict(scope.get('headers', []))
            auth_header = headers.get(b'authorization', b'').decode()
            
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        scope['user'] = AnonymousUser()
        
        if token:
            try:
                # Decode the token
                decoded_token = jwt_decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = decoded_token.get('user_id')
                
                if user_id:
                    scope['user'] = await get_user(user_id)
            except InvalidTokenError:
                pass
        
        return await super().__call__(scope, receive, send)
