from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from .models import CustomUser
from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack
from django.db import close_old_connections
from urllib.parse import parse_qs
from jwt import ExpiredSignatureError, decode as jwt_decode
from django.conf import settings
import requests


@database_sync_to_async
def get_user(validated_token):
    try:
        user = get_user_model().objects.get(id=validated_token["user_id"])
        # return get_user_model().objects.get(id=toke_id)
        print(f"{user}")
        return user
   
    except CustomUser.DoesNotExist:
        return AnonymousUser()


class JwtAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
       # Close old database connections to prevent usage of timed out connections
        close_old_connections()

        # Get the token
        token = parse_qs(scope["query_string"].decode("utf8"))["token"][0]

        # Try to authenticate the user
        try:
            # This will automatically validate the token and raise an error if token is invalid
            UntypedToken(token)
        except (InvalidToken, TokenError) as e:
            # Token is invalid
            print(e)
            return None
        else:
            #  Then token is valid, decode it
            decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            print(decoded_data)
            # Will return a dictionary like -
            # {
            #     "token_type": "access",
            #     "exp": 1568770772,
            #     "jti": "5c15e80d65b04c20ad34d77b6703251b",
            #     "user_id": 6
            # }

            # Get the user using ID
            scope["user"] = await get_user(validated_token=decoded_data)
        return await super().__call__(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(AuthMiddlewareStack(inner))
# from channels.db import database_sync_to_async
# from django.contrib.auth import get_user_model
# from django.contrib.auth.models import AnonymousUser
# from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
# from rest_framework_simplejwt.tokens import UntypedToken
# from channels.middleware import BaseMiddleware
# from channels.auth import AuthMiddlewareStack
# from django.db import close_old_connections
# from urllib.parse import parse_qs
# from jwt import decode as jwt_decode, ExpiredSignatureError
# from django.conf import settings
# from .models import CustomUser
# import requests
# from datetime import datetime, timezone


# @database_sync_to_async
# def get_user_from_token(user_id):
#     try:
#         return get_user_model().objects.get(id=user_id)
#     except CustomUser.DoesNotExist:
#         return AnonymousUser()


# def decode_jwt_token(token):
#     try:
#         decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
#         return decoded_data
#     except ExpiredSignatureError:
#         print("Token has expired")
#         return None
#     except Exception as e:
#         print(f"JWT decoding error: {e}")
#         return None


# def validate_token(token):
#     try:
#         UntypedToken(token)
#         return True
#     except ExpiredSignatureError:
#         print("Token has expired, attempting to refresh...")
#         return False
#     except (InvalidToken, TokenError) as e:
#         print(f"Token validation error: {e}")
#         return False


# def refresh_access_token(refresh_token):
#     """
#     Uses the refresh token to get a new access token from the refresh endpoint.
#     Returns the new access token or None if the refresh fails.
#     """
#     try:
#         response = requests.post(
#             f"http://127.0.0.1:8000/auth/token/refresh/",
#             data={'refresh': refresh_token}
#         )
#         if response.status_code == 200:
#             return response.json().get('access')
#         else:
#             print("Failed to refresh access token")
#             return None
#     except Exception as e:
#         print(f"Error refreshing token: {e}")
#         return None


# class JwtAuthMiddleware(BaseMiddleware):
#     def __init__(self, inner):
#         super().__init__(inner)

#     async def __call__(self, scope, receive, send):
#         close_old_connections()

#         token = parse_qs(scope["query_string"].decode("utf8")).get("token", [None])[0]

#         if token:
#             if validate_token(token):
#                 decoded_data = decode_jwt_token(token)
#                 if decoded_data:
#                     scope["user"] = await get_user_from_token(user_id=decoded_data["user_id"])
#                 else:
#                     scope["user"] = AnonymousUser()
#             else:
#                 # Attempt to refresh the token if expired
#                 refresh_token = parse_qs(scope["query_string"].decode("utf8")).get("refresh_token", [None])[0]
#                 if refresh_token:
#                     new_access_token = refresh_access_token(refresh_token)
#                     if new_access_token:
#                         decoded_data = decode_jwt_token(new_access_token)
#                         if decoded_data:
#                             scope["user"] = await get_user_from_token(user_id=decoded_data["user_id"])
#                         else:
#                             scope["user"] = AnonymousUser()
#                     else:
#                         scope["user"] = AnonymousUser()
#                 else:
#                     scope["user"] = AnonymousUser()
#         else:
#             scope["user"] = AnonymousUser()

#         return await super().__call__(scope, receive, send)


# def JwtAuthMiddlewareStack(inner):
#     return JwtAuthMiddleware(AuthMiddlewareStack(inner))
