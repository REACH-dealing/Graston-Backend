from rest_framework import serializers
from .models import SessionType, Session, SessionPackage


class SessionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionType
        fields = '__all__'


class SessionPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionPackage
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'




