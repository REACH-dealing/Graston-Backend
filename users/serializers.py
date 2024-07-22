from rest_framework import serializers
from .models import User, Patient, Nurse, Admin, Session


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
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
            "identity",
            "gender",
            "phone_number",
            "bio",
            "nationality",
            "location",
            "city",
            "country",
            "date_of_birth",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        """
        Encrypt password.
        """
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for patient model
    """
    
    class Meta:
        model = Patient
        fields = [
            "profile_image",
            "chronic_diseases",
            "medical_report",
        ]


class NurseSerializer(serializers.ModelSerializer):
    """
    Serializer for Nurse model
    """
    
    class Meta:
        model = Nurse
        fields = [
            "profile_image",
            "specialization",
            "certificates",
            "medical_accreditations",
            "available_working_hours"
        ]


class AdminSerializer(serializers.ModelSerializer):
    """
    Serializer for Admin model
    """
    
    class Meta:
        model = Admin
        fields = ["profile_image"]


class SessionSerializer(serializers.ModelSerializer):
    """
    Serializer for Session model.
    """

    class Meta:
        model = Session
        fields = [
            "patient",
            "nurse",
            "price",
            "remaining_price",
            "total_sessions",
            "remaining_sessions",
            "prev_session",
            "next_session",
            "place",
            "start_time",
            "end_time",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }