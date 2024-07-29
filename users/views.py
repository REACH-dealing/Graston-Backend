from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserNoDataSerializer, UserSerializer, UserEmailSerializer
from .models import User
import jwt, datetime
from rest_framework import status
from rest_framework import viewsets, pagination
from Graston.settings import SECRET_KEY
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random

class RegisterView(viewsets.ModelViewSet):
    """
    Create a new user.
    """

    queryset = User.objects.none()
    serializer_class = UserRegisterSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"Register Success": "Activate your accout"})


class VerifyEmail(viewsets.ModelViewSet):
    """
    Verify Email.
    """

    queryset = User.objects.all()
    serializer_class = UserEmailSerializer

    def verify_email(self, request, email):
        """
        Verify Email.
        """
        code = random.randint(1000, 9999)

        # Load the HTML content from a template file
        html_content = render_to_string('verification_email.html', {'code': code})
        plain_message = strip_tags(html_content)  # Fallback for plain-text email

        send_mail(
            subject="Activate your Graston account",
            message=plain_message,
            from_email=None,
            recipient_list=[email],
            html_message=html_content,
            fail_silently=False,
        )
        return Response(f"We sent a code number to your email: {email}")


def get_tokens(user):

    access_payload = {
        "user_id": user.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=61),
        "iat": datetime.datetime.utcnow(),
        "refresh": False,
    }

    refresh_payload = {
        "user_id": user.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=70),
        "iat": datetime.datetime.utcnow(),
        "refresh": True,
    }

    # remember to search about best encoding algorithm & add the algorithm name to .env file
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm="HS256")

    return access_token, refresh_token


class LoginView(viewsets.ModelViewSet):
    """
    User Login.
    """

    queryset = User.objects.all()
    serializer_class = UserLoginSerializer

    def login(self, request):
        """
        User Login.

        Returns:
            {"access": access_token, "refresh": refresh_token } in
            json format and in cookie.
        """
        email = request.data["email"]
        password = request.data["password"]

        user = self.get_queryset().filter(email=email).first()

        if not user:
            raise AuthenticationFailed("User not found!")

        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password!")

        if not user.is_active:
            raise AuthenticationFailed("Account disabled, contact admin")

        # if not user.is_verified:
        #     raise AuthenticationFailed("Email is not verified, activate your account")

        access_token, refresh_token = get_tokens(user)
        response = Response()
        response.set_cookie(key="access", value=access_token, httponly=True)
        response.set_cookie(key="refresh", value=refresh_token, httponly=True)
        response.data = {"access": access_token, "refresh": refresh_token}
        return response


class RefreshTokenView(viewsets.ModelViewSet):
    """
    Refresh token.
    """

    queryset = User.objects.all()
    serializer_class = UserNoDataSerializer

    def refresh_token(self, request):
        """
        Refresh token.

        Returns:
            {"access": access_token, "refresh": refresh_token } in
            json format and in cookie.
        """

        # remember to search which is best method for auth (cookies or header)
        token = request.headers.get("Authorization") or request.COOKIES.get("refresh")

        if not token:
            return JsonResponse({"detail": "There is no refresh token"})

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        except jwt.ExpiredSignatureError:
            return JsonResponse({"detail": "Token is expired!"})

        except jwt.exceptions.DecodeError as identifier:
            return JsonResponse({'error': 'Invalid token'})

        if payload["refresh"] == False:
            return JsonResponse({"detail": "This is not refresh token, you must send refresh token!"})

        user = User.objects.filter(id=payload["user_id"]).first()
        if not user:
            return JsonResponse({"detail": "Unauthenticated!"})

        access_token, refresh_token = get_tokens(user)
        response = Response()
        response.set_cookie(key="access", value=access_token, httponly=True)
        response.set_cookie(key="refresh", value=refresh_token, httponly=True)
        response.data = {"access": access_token, "refresh": refresh_token}
        return response


class UserView(viewsets.ModelViewSet):
    """
    Check Authentication and Retrieve User.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request):
        """
        Retrieve Login User data after checking authentication.
        """
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)


class LogoutView(viewsets.ModelViewSet):
    """
    User Logout and Delete Cookie.
    """

    queryset = User.objects.all()
    serializer_class = UserNoDataSerializer

    def logout(self, request):
        """
        User Logout and Delete Cookie.

        Note: request body is not required.
        """
        response = Response()
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        response.data = {"message": "success"}
        return response


# class UserViewSet(viewsets.ModelViewSet):
#     """
#     User CRUD
#     """

#     queryset = User.objects.all()
#     serializer_class = UserSerializer

#     def list(self, request):
#         """
#         List Users.
#         """

#         user = self.get_queryset()
#         serializer = self.serializer_class(user, many=True)
#         return Response(serializer.data)

#     def retrieve(self, request, pk):
#         """
#         Retrieve user by id.
#         """

#         user = self.get_queryset().filter(id=pk).first()
#         serializer = self.serializer_class(user)
#         return Response(serializer.data)

#     def update(self, request, pk):
#         """
#         Update User.
#         """
#         user = self.get_queryset().filter(id=pk).first()
#         if user is not None:
#             if request.user.id != user.id:
#                 return Response(
#                     "You are not authorized to update this data",
#                     status=status.HTTP_403_FORBIDDEN,
#                 )
#         serializer = self.serializer_class(user, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     def destroy(self, request, pk):
#         """
#         Delete User.
#         """
#         user = self.get_queryset().filter(id=pk).first()
#         if user is not None:
#             if request.user.id != user.id:
#                 return Response(
#                     "You are not authorized to delete this user",
#                     status=status.HTTP_403_FORBIDDEN,
#                 )
#         user.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class UserPagination(pagination.PageNumberPagination):
#     """
#     Pagination class for User objects.

#     This class defines the page size for paginated responses.

#     Attributes:
#         page_size (int): The number of users to display per page.
#             Default is 10.
#     """

#     page_size = 10


# class UserSearch(viewsets.ModelViewSet):
#     """
#     Search Users and list them by pagination pages.
#     """

#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     pagination_class = UserPagination

#     def list(self, request, string):
#         """
#         Search users and list them by pagination pages(10 by 10).

#         Note: the input string search can be near from the actual string.
#         """

#         queryset = (
#             self.get_queryset().filter(name__icontains=string)
#             | self.get_queryset().filter(name__trigram_similar=string)
#             | self.get_queryset().filter(name__unaccent=string)
#         )
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)

#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
