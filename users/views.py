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
    PasswordChangeSerializer,
    PasswordVerificationSerializer,
    PatientSerializer,
    NurseSerializer,

)
from .models import User, VerificationRequests, Patient, Nurse
from rest_framework import status, generics
from rest_framework import viewsets, pagination
import jwt, datetime
from Graston.settings import SECRET_KEY
from .utils import get_tokens, regenerate_otp, send_otp2email_util


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

    def send_otp2phone(self, request, user_id):
        pass
        # """
        # send otp number to Phone.
        # """
        # response = self.regenerate_otp(request, user_id)
        # if response is not None:
        #     return response

        # return send_otp2phone_util(user_id, "verification_email.html")

    def send_otp2email(self, request, user_id):
        """
        send otp number to Email.
        """

        try:
            instnace = VerificationRequests.objects.create(user=user_id)
        except:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)
        
        response = regenerate_otp(instnace)

        if response is not None:
            return response

        try:
            instnace = VerificationRequests.objects.filter(user=user_id).order_by("-created_at").last()
        except:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)


        return send_otp2email_util(instnace, "verification_email.html")

    def verify_otp(self, request, user_id):
        """
        check that otp number is correct.
        """

        try:
            user = User.objects.filter(id=user_id).first()
        except:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)

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

# 0) patient registration
# 0) nurse registration


# 1) delete account (soft delete)
# 2) activate account ()
# 3) get patient or nurse data
# 4) update patient or nurse data:
#       A@password change@ -send old and new password-,
#       B@email change@ -send password and verify email-,
#       C@phone number change@ -send password and verify phone-,
#       D@other data change@ -send password and new data-
#   NOTE: no identity Update


class SoftDeleteAccountView(generics.DestroyAPIView):
    queryset = User.objects.filter(is_active=True)
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        
        user.is_active = False
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
    

class RectivateAccountView(generics.GenericAPIView):
    queryset = User.objects.filter(is_active=False)
    
    def post(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = True
        user.save()

        return Response({"message": "Account Reactivated"}, status=status.HTTP_200_OK)
    

class PatientDetailsView(generics.RetrieveAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

class NurseDetailsView(generics.RetrieveAPIView):
    queryset = Nurse.objects.all()
    serializer_class = NurseSerializer


class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"detail": "Password has been changed."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CheckPasswordView(generics.GenericAPIView):
    serializer_class = PasswordVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            password = serializer.validated_data["password"]

            if user.check_password(password):
                return Response({"detail": "Password is correct."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)