import jwt
from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed
from rest_framework import status
from django.http import JsonResponse
from users.models import User
import Graston.settings

class AuthenticationMiddleware(MiddlewareMixin):
    EXEMPT_PATHS = [
        "",
        "/auth/register/",
        "/auth/login/",
        "/api/schema/",
        "/api/schema/swagger-ui/",
        "/api/schema/redoc/",
    ]

    def process_request(self, request):
        if any(
            request.path.startswith(exempt_path) for exempt_path in self.EXEMPT_PATHS
        ):
            return None

        token = request.headers.get("Authorization") or request.COOKIES.get("access")

        if not token:
            return JsonResponse({"detail": "Invalid token"})

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        except jwt.ExpiredSignatureError:
            return JsonResponse({"detail": "Token is expired!"})

        except jwt.exceptions.DecodeError as identifier:
            return JsonResponse({'error': 'Invalid token'})
        
        if payload["refresh"] == True:
            return JsonResponse({"detail": "This is refresh token, you must send access token!"})

        user = User.objects.filter(id=payload["user_id"]).first()
        if not user:
            return JsonResponse({"detail": "Unauthenticated!"})

        request.user = user
