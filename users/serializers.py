from rest_framework import serializers
from django.db import transaction
from .models import User, Patient, Nurse, Admin, VerificationRequests

from django.contrib.auth.hashers import check_password
from django.contrib.auth import password_validation

from django.core.validators import validate_email


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for User Registeration.
    """
    password = serializers.CharField(max_length=128)
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
            "profile_image",
        ]
        extra_kwargs = {
            "identity": {"read_only": True},
            "password": {"required": True, "write_only": True},
            "national_id": {"required": True},
            "username": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
            "gender": {"required": True},
            "location": {"required": True},
            "city": {"required": True},
            "country": {"required": True},
            "date_of_birth": {"required": True},
        }

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value


class PatientRegisterSerializer(serializers.ModelSerializer):
    user = UserRegisterSerializer()

    class Meta:
        model = Patient
        fields = ['user', 'chronic_diseases', 'medical_report']

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        user.set_password(user_data['password'])
        user.identity = "P"
        user.save()
        patient = Patient.objects.create(user=user, **validated_data)
        return patient

class NurseRegisterSerializer(serializers.ModelSerializer):
    user = UserRegisterSerializer()

    class Meta:
        model = Nurse
        fields = ['user', 'specialization', 'certificates', 'medical_accreditations', 'available_working_hours']

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        user.set_password(user_data['password'])
        user.identity = "D"
        user.save()
        nurse = Nurse.objects.create(user=user, **validated_data)
        return nurse


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
        model = VerificationRequests
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



class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Patient
        fields = ('user', 'chronic_diseases', 'medical_report')


class NurseSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Nurse
        fields = ('user', 'specialization', 'certificates', 'medical_accreditations', 'available_working_hours')

    
class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not check_password(value, user.password):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value
    
class PasswordVerificationSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)

class VerifcationRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationRequests
        fields = "__all__"


        
class EmailChangeSerializer(serializers.Serializer):
    new_email = serializers.EmailField(max_length=63, validators=[validate_email])
    