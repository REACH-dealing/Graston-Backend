import datetime
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework import viewsets, pagination
from .serializers import (
    PatientRegisterSerializer,
    NurseRegisterSerializer,
    UserLoginSerializer,
    UserNoDataSerializer,
    UserSerializer,
    OTPSerializer,
    PasswordChangeSerializer,
    PasswordVerificationSerializer,
    PatientSerializer,
    NurseSerializer,
    EmailSerializer,
    PasswordForgetSerializer,
    UpdateUserProfileSerializer,
    UpdatePatientProfileSerialzier,
    UpdateNurseProfileSerializer,
    WorkHoursSerializer,
    WorkHoursSerializer,
)
from .models import User, VerificationRequests, Patient, Nurse, WorkAvailableHours
from .utils import get_tokens, regenerate_otp, send_otp2email_util
from Graston.settings import SECRET_KEY


class PatientRegisterView(generics.CreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientRegisterSerializer


class NurseRegisterView(generics.CreateAPIView):
    queryset = Nurse.objects.all()
    serializer_class = NurseRegisterSerializer


class VerifyAccount(viewsets.ModelViewSet):
    """
    Verify Account.
    """

    queryset = User.objects.all()
    serializer_class = OTPSerializer

    def send_otp2phone(self, request, user_id):
        pass

    def send_otp2email(self, request, user_id):
        """
        send otp number to Email.
        """

        try:
            user = User.objects.filter(id=user_id).first()
        except:
            return Response("User not found created ", status=status.HTTP_404_NOT_FOUND)

        instance = VerificationRequests.objects.create(user=user, email=user.email)
        response, instance = regenerate_otp(instance)

        if response is not None:
            return response

        return send_otp2email_util(instance, "verification_email.html")

    def verify_otp(self, request, user_id):
        """
        check that otp number is correct.
        """

        try:
            instance = VerificationRequests.objects.filter(user__id=user_id).last()
        except:
            return Response(
                "no object matches this id", status=status.HTTP_404_NOT_FOUND
            )

        # if user.is_verified == True:
        #     return Response("Your account is already verified.", status=status.HTTP_400_BAD_REQUEST)
        if instance.otp != request.data.get("otp"):
            return Response(
                "Please enter the correct OTP", status=status.HTTP_400_BAD_REQUEST
            )
        if (
            instance.otp_expiry
            and datetime.datetime.now(datetime.UTC) < instance.otp_expiry
        ):
            request.user.is_verified = True
            instance.otp_expiry = None
            instance.otp_max_try = 3
            instance.otp_max_out = None
            instance.otp_done = True
            instance.save()

            user = request.user
            user.email = instance.email
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


# class RefreshTokenView(viewsets.ModelViewSet):
#     """
#     Refresh token.
#     """

#     queryset = User.objects.all()
#     serializer_class = UserNoDataSerializer

#     def refresh_token(self, request):
#         """
#         Refresh token.

#         Returns:
#             {"access": access_token, "refresh": refresh_token } in
#             json format and in cookie.
#         """

#         # remember to search which is best method for auth (cookies or header)
#         token = request.headers.get("Authorization") or request.COOKIES.get("refresh")

#         if not token:
#             return JsonResponse({"detail": "There is no refresh token"})

#         try:
#             payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

#         except jwt.ExpiredSignatureError:
#             return JsonResponse({"detail": "Token is expired!"})

#         except jwt.exceptions.DecodeError as identifier:
#             return JsonResponse({"error": "Invalid token"})

#         if payload["refresh"] == False:
#             return JsonResponse(
#                 {"detail": "This is not refresh token, you must send refresh token!"}
#             )

#         user = User.objects.filter(id=payload["user_id"]).first()
#         if not user:
#             return JsonResponse({"detail": "Unauthenticated!"})

#         access_token, refresh_token = get_tokens(user)
#         response = Response()
#         response.set_cookie(key="access", value=access_token, httponly=True)
#         response.set_cookie(key="refresh", value=refresh_token, httponly=True)
#         response.data = {"access": access_token, "refresh": refresh_token}
#         return response


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


class SoftDeleteAccountView(generics.DestroyAPIView):
    queryset = User.objects.filter(is_active=True)

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RectivateAccountView(generics.GenericAPIView):
    queryset = User.objects.filter(is_active=False)

    # serializer_class =
    def post(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = True
        user.save()

        return Response({"message": "Account Reactivated"}, status=status.HTTP_200_OK)


class PatientDetailsView(generics.RetrieveAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def get_object(self):
        user_id = self.kwargs.get("pk")

        return Patient.objects.get(user__id=user_id)


class NurseDetailsView(generics.RetrieveAPIView):
    queryset = Nurse.objects.all()
    serializer_class = NurseSerializer

    def get_object(self):
        user_id = self.kwargs.get("pk")

        return Nurse.objects.get(user__id=user_id)


class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(
                {"detail": "Password has been changed."}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckPasswordView(generics.GenericAPIView):
    serializer_class = PasswordVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            password = serializer.validated_data["password"]

            if user.check_password(password):
                return Response(
                    {"detail": "Password is correct."}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"detail": "Password is incorrect."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeEmailView(generics.GenericAPIView):
    serializer_class = EmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            new_email = serializer.validated_data["new_email"]
            check_if_unique = User.objects.filter(email=new_email)

            if check_if_unique:
                return Response(
                    {"message": "Email already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            instance = VerificationRequests.objects.create(user=user, email=new_email)
            response, instance = regenerate_otp(instance)

            if response is not None:
                return response

            return send_otp2email_util(instance, "verification_new_email.html")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordView(generics.GenericAPIView):
    serializer_class = EmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = User.objects.get(email=email)

            instance = VerificationRequests.objects.create(user=user, email=email)
            response, instance = regenerate_otp(instance)

            if response is not None:
                return response

            return send_otp2email_util(instance, "verification_new_email.html")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckOTPtoChangePassword(generics.GenericAPIView):
    serializer_class = OTPSerializer

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs.get("user_id")
        try:
            instance = VerificationRequests.objects.filter(user__id=user_id).last()
        except:
            return Response(
                "no object matches this id", status=status.HTTP_404_NOT_FOUND
            )

        # if user.is_verified == True:
        #     return Response("Your account is already verified.", status=status.HTTP_400_BAD_REQUEST)
        if instance.otp != request.data.get("otp"):
            return Response(
                "Please enter the correct OTP", status=status.HTTP_400_BAD_REQUEST
            )
        if (
            instance.otp_expiry
            and datetime.datetime.now(datetime.UTC) < instance.otp_expiry
        ):
            request.user.is_verified = True
            instance.otp_expiry = None
            instance.otp_max_try = 3
            instance.otp_max_out = None
            instance.otp_done = True
            instance.save()

            return Response("OTP is correct", status=status.HTTP_200_OK)
        else:
            return Response("OTP is expired", status=status.HTTP_400_BAD_REQUEST)


class ConfirmForgetPassword(generics.GenericAPIView):
    serializer_class = PasswordForgetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user_id = self.kwargs.get("user_id")
            user = User.objects.get(id=user_id)

            verify_request = VerificationRequests.objects.filter(
                user__id=user_id
            ).last()

            if verify_request.otp_done:
                password = serializer.validated_data["new_password"]
                user.set_password(password)
                user.save()

                return Response(
                    {"message": "Password reset succuessfuly"},
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"message": "Enter correct OTP"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserProfileView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UpdateUserProfileSerializer
    http_method_names = ["patch"]


class UpdatePatientProfileView(generics.UpdateAPIView):
    queryset = Patient.objects.all()
    serializer_class = UpdatePatientProfileSerialzier
    http_method_names = ["patch"]

    def get_object(self):
        user_id = self.kwargs.get("pk")

        return Patient.objects.get(user__id=user_id)


class UpdateNurseProfileView(generics.UpdateAPIView):
    queryset = Nurse.objects.all()
    serializer_class = UpdateNurseProfileSerializer
    http_method_names = ["patch"]

    def get_object(self):
        user_id = self.kwargs.get("pk")

        return Nurse.objects.get(user__id=user_id)


class WorkHoursViewSet(viewsets.ModelViewSet):
    queryset = WorkAvailableHours.objects.all()
    serializer_class = WorkHoursSerializer
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self):
        nurse = self.request.user.nurse
        return WorkAvailableHours.objects.filter(nurse=nurse)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(nurse=request.user.nurse)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data)
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
