from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserNoDataSerializer,
    UserSerializer,
    OTPSerializer,
)
from .models import User
from rest_framework import status
from rest_framework import viewsets, pagination
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from Graston.settings import SECRET_KEY
from .utils import get_tokens
import jwt, datetime
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


class VerifyAccount(viewsets.ModelViewSet):
    """
    Verify Account.
    """

    queryset = User.objects.all()
    serializer_class = OTPSerializer

    def regenerate_otp(self, request, email):
        """
        Regenerate OTP for the given user.
        """

        try:
            user = User.objects.filter(email=email).first()
        except:
            return Response(
                "Enter your correct email you used to register",
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            user.otp_max_try == 0
            and datetime.datetime.now(datetime.UTC) < user.otp_max_out
        ):
            return Response(
                "Max OTP try reached, try after a three minutes",
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.otp = random.randint(1000, 9999)
        user.otp_expiry = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            minutes=2
        )
        user.otp_max_try = user.otp_max_try - 1
        if user.otp_max_try == 0:
            # Remember to edit max out to one hour
            user.otp_max_out = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
                minutes=3
            )

        elif user.otp_max_try == -1:
            user.otp_max_try = 3

        else:
            user.otp_max_out = None
            # user.otp_max_try = user.otp_max_try

        user.save()
        # send_otp(user.phone_number, user.otp)

        # return Response("Successfully generate new OTP.", status=status.HTTP_200_OK)

    def send_otp2email(self, request, email):
        """
        send otp number to Email.
        """
        response = self.regenerate_otp(request, email)
        if response is not None:
            return response

        try:
            user = User.objects.filter(email=email).first()
        except:
            return Response(
                "Enter your correct email you used to register",
                status=status.HTTP_404_NOT_FOUND,
            )

        # Load the HTML content from a template file
        html_content = render_to_string("verification_email.html", {"otp": user.otp})
        plain_message = strip_tags(html_content)  # Fallback for plain-text email

        try:
            send_mail(
                subject="Activate your Graston account",
                message=plain_message,
                from_email=None,
                recipient_list=[email],
                html_message=html_content,
                fail_silently=False,
            )
            return Response(f"We sent otp number to your email: {email}")

        except Exception as e:
            return Response(e)

    def verify_otp(self, request, email):
        """
        check that otp number is correct.
        """

        try:
            user = User.objects.filter(email=email).first()
        except:
            return Response(
                "Enter your correct email you used to register",
                status=status.HTTP_404_NOT_FOUND,
            )

        # if user.is_verified == True:
        #     return Response("Your account is already verified.", status=status.HTTP_400_BAD_REQUEST)
        if user.otp != request.data.get("otp"):
            return Response(
                "Please enter the correct OTP", status=status.HTTP_400_BAD_REQUEST
            )
        if user.otp_expiry and datetime.datetime.now(datetime.UTC) < user.otp_expiry:
            user.is_verified = True
            user.otp_expiry = None
            user.otp_max_try = 3
            user.otp_max_out = None
            user.save()
            return Response(
                "Successfully verified your account", status=status.HTTP_200_OK
            )
        else:
            return Response("OTP is expired", status=status.HTTP_400_BAD_REQUEST)


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
            return JsonResponse({"error": "Invalid token"})

        if payload["refresh"] == False:
            return JsonResponse(
                {"detail": "This is not refresh token, you must send refresh token!"}
            )

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
