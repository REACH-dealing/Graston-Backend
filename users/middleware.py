# import jwt
# from django.utils.deprecation import MiddlewareMixin
# from django.http import JsonResponse
# from users.models import User


# class AuthenticationMiddleware(MiddlewareMixin):
#     EXEMPT_PATHS = [
#         "/auth/register/",
#         "/auth/login/",
#         "/api/schema/",
#         "/api/schema/swagger-ui/",
#         "/api/schema/redoc/",
#     ]

#     def process_request(self, request):
#         if any(
#             request.path.startswith(exempt_path) for exempt_path in self.EXEMPT_PATHS
#         ):
#             return None

#         token = request.headers.get("Authorization") or request.COOKIES.get("jwt")

#         if not token:
#             return JsonResponse({"detail": "Unauthenticated!"}, status=403)

#         try:
#             payload = jwt.decode(token, "secret", algorithms=["HS256"])
#         except jwt.ExpiredSignatureError:
#             return JsonResponse({"detail": "Unauthenticated!"}, status=403)

#         user = User.objects.filter(id=payload["id"]).first()
#         if not user:
#             return JsonResponse({"detail": "Unauthenticated!"}, status=403)

#         request.user = user
