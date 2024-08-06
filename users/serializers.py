import random
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.hashers import check_password
from django.contrib.auth import password_validation
from django.core.validators import validate_email
from .models import (
    User,
    Patient,
    Nurse,
    Admin,
    VerificationRequests,
    WorkAvailableHours,
)


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for User Registeration.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "national_id",
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
            "identity": {"read_only": True},
            "password": {"required": True, "write_only": True},
            "national_id": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
            "gender": {"required": True},
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
        fields = [
            "user",
            "chronic_diseases",
            "medical_report",
        ]

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = User.objects.create(**user_data)
        user.set_password(user_data["password"])
        user.identity = "P"
        user.username = (
            user_data["first_name"]
            + "_"
            + user_data["last_name"]
            + "_"
            + str(random.randint(1000, 9999))
        )
        user.save()
        patient = Patient.objects.create(user=user, **validated_data)
        return patient


class NurseRegisterSerializer(serializers.ModelSerializer):
    user = UserRegisterSerializer()

    class Meta:
        model = Nurse
        fields = [
            "user",
            "specialization",
            "certificates",
            "medical_accreditations",
        ]

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = User.objects.create(**user_data)
        user.set_password(user_data["password"])
        user.identity = "D"
        user.username = (
            user_data["first_name"]
            + "_"
            + user_data["last_name"]
            + "_"
            + str(random.randint(1000, 9999))
        )
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
        fields = [
            "email",
            "password",
        ]
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


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Patient
        fields = [
            "user",
            "chronic_diseases",
            "medical_report",
        ]


class NurseSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Nurse
        fields = [
            "user",
            "specialization",
            "certificates",
            "medical_accreditations",
        ]


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
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


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=63, validators=[validate_email])


class PasswordForgetSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value


## update city, country, profile_image
## update patient and nurse data


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "profile_image",
            "city",
            "country",
        ]


class UpdatePatientProfileSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            "chronic_diseases",
            "medical_report",
        ]


class UpdateNurseProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nurse
        fields = [
            "specialization",
            "certificates",
            "medical_accreditations",
        ]


class WorkHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkAvailableHours
        fields = [
            "id",
            "day",
            "start_time",
            "end_time",
        ]

        extra_kwargs = {"id": {"read_only": True}}

    def validate(self, data):
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("Start time must be before end time.")

        return data
