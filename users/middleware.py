import jwt
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework import status
from users.models import User
from Graston.settings import SECRET_KEY


class AuthenticationMiddleware(MiddlewareMixin):
    EXEMPT_PATHS = [
        "/auth/register/",
        "/auth/login/",
        "/auth/refresh-token/",
        "/auth/send-otp2email/",
        "/auth/verify-email/",
        "/api/schema/",
        "/api/schema/swagger-ui/",
        "/api/schema/redoc/",
    ]

    def process_request(self, request):
        if any(
            request.path.startswith(exempt_path) for exempt_path in self.EXEMPT_PATHS
        ):
            return None

        # remember to search which is best method for auth (cookies or header)
        token = request.headers.get("Authorization") or request.COOKIES.get("access")

        if not token:
            return JsonResponse(
                {"detail": "There is no access token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        except jwt.ExpiredSignatureError:
            return JsonResponse(
                {"detail": "Token is expired!"}, status=status.HTTP_401_UNAUTHORIZED
            )

        except jwt.exceptions.DecodeError as identifier:
            return JsonResponse(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

        if payload["refresh"] == True:
            return JsonResponse(
                {"detail": "This is refresh token, you must send access token!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(id=payload["user_id"]).first()
        if not user:
            return JsonResponse(
                {"detail": "Unauthenticated!"}, status=status.HTTP_401_UNAUTHORIZED
            )

        request.user = user
