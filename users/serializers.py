from rest_framework import serializers
from django.db import transaction
from .models import User, Patient, Nurse, Admin, VerificationRequests


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for User Registeration.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "national_id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "phone_number",
            "identity",
            "gender",
            "location",
            "city",
            "country",
            "date_of_birth",
            "nationality",
        ]
        extra_kwargs = {
            "password": {"required": True, "write_only": True},
            "national_id": {"required": True},
            "username": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
            "identity": {"required": True},
            "gender": {"required": True},
            "location": {"required": True},
            "city": {"required": True},
            "country": {"required": True},
            "date_of_birth": {"required": True},
        }

    @transaction.atomic
    def create(self, validated_data):
        """
        Create User.
        """

        user = User.objects.create_user(**validated_data)

        if user.identity == "Patient" or user.identity == "P":
            Patient.objects.create(user=user)
        elif user.identity == "Nurse" or user.identity == "D":
            Nurse.objects.create(user=user)

        return user
        # password = validated_data.pop("password", None)
        # instance = self.Meta.model(**validated_data)
        # if password is not None:
        #     instance.set_password(password)
        # instance.save()
        # return instance


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "national_id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "identity",
            "gender",
            "location",
            "city",
            "country",
            "date_of_birth",
            "nationality",
            "bio",
            "profile_image",
        ]


class UserLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["email", "password"]
        extra_kwargs = {
            "password": {"required": True, "write_only": True},
            "email": {"required": True},
        }


class UserNoDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = []


class OTPSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["otp"]


# class PatientSerializer(serializers.ModelSerializer):
#     """
#     Serializer for patient model
#     """

#     class Meta:
#         model = Patient
#         fields = [
#             "user",
#             "profile_image",
#             "chronic_diseases",
#             "medical_report",
#         ]


# class NurseSerializer(serializers.ModelSerializer):
#     """
#     Serializer for Nurse model
#     """

#     class Meta:
#         model = Nurse
#         fields = [
#             "user",
#             "profile_image",
#             "specialization",
#             "certificates",
#             "medical_accreditations",
#             "available_working_hours"
#         ]


# class AdminSerializer(serializers.ModelSerializer):
#     """
#     Serializer for Admin model
#     """

#     class Meta:
#         model = Admin
#         fields = ["user"]


# # class AbstractSessionSerializer(serializers.ModelSerializer):
# #     """
# #     Serializer for AbstractSession model.
# #     """

# #     class Meta:
# #         model = AbstractSession
# #         fields = [
# #             "id",
# #             "session_type",
# #             "price",
# #         ]


# # class SessionSerializer(serializers.ModelSerializer):
# #     """
# #     Serializer for Session model.
# #     """

# #     class Meta:
# #         model = Session
# #         fields = [
# #             "id",
# #             "session_type",
# #             "price",
# #             "patient",
# #             "nurse",
# #             "paid_price",
# #             "total_sessions",
# #             "remaining_sessions",
# #             "prev_session",
# #             "next_session",
# #             "place",
# #             "start_time",
# #             "end_time",
# #         ]
# #         extra_kwargs = {
# #             "session_type": {"read_only": True},
# #             "price": {"read_only": True},
# #         }


class VerifcationRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationRequests
        fields = "__all__"