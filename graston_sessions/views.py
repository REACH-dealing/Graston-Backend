from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.response import Response

from rest_framework.permissions import IsAdminUser

from .models import Session, SessionPackage, SessionType
from .serializers import SessionTypeSerializer, SessionPackageSerializer, SessionSerializer


 ############ Session Type

class SessionTypeCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = SessionTypeSerializer
    queryset = SessionType.objects.all()


class SessionTypeUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = SessionTypeSerializer
    queryset = SessionType.objects.all()


class SessionTypeDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = SessionTypeSerializer
    queryset = SessionType.objects.all()

class SessionTypeListView(generics.ListAPIView):
    serializer_class = SessionTypeSerializer
    queryset = SessionType.objects.all()


class SessionTypeRetrieveView(generics.RetrieveAPIView):
    serializer_class = SessionTypeSerializer
    queryset = SessionType.objects.all()


############## Session Package 

class SessionPackageCreateView(generics.CreateAPIView):
    # permission_classes = [IsAdminUser]
    serializer_class = SessionPackageSerializer
    queryset = SessionPackage.objects.all()


class SessionPackageUpdateView(generics.UpdateAPIView):
    # permission_classes = [IsAdminUser]
    serializer_class = SessionPackageSerializer
    queryset = SessionPackage.objects.all()


class SessionPackageDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = SessionPackageSerializer
    queryset = SessionPackage.objects.all()

class SessionPackageListView(generics.ListAPIView):
    serializer_class = SessionPackageSerializer
    queryset = SessionPackage.objects.all()


class SessionPackageRetrieveView(generics.RetrieveAPIView):
    serializer_class = SessionPackageSerializer
    queryset = SessionPackage.objects.all()


############################### Session

class SessionCreateView(generics.CreateAPIView):
    # permission_classes = [IsAdminUser]
    serializer_class = SessionSerializer
    queryset = Session.objects.all()


class SessionUpdateView(generics.UpdateAPIView):
    # permission_classes = [IsAdminUser]
    serializer_class = SessionSerializer
    queryset = Session.objects.all()


class SessionDeleteView(generics.DestroyAPIView):
    # permission_classes = [IsAdminUser]
    serializer_class = SessionSerializer
    queryset = Session.objects.all()

class SessionListView(generics.ListAPIView):
    serializer_class = SessionSerializer
    queryset = Session.objects.all()


class SessionRetrieveView(generics.RetrieveAPIView):
    serializer_class = SessionSerializer
    queryset = Session.objects.all()


#######################################################################
## Cancel Session 

class CancelSessionView(generics.GenericAPIView):
    serializer_class = SessionSerializer
    queryset = Session.objects.all()

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        instance.status = "cancelled"
        instance.save()
        
        return Response({"id": serializer.data["id"], "status": serializer.data["status"]}, status=status.HTTP_200_OK)
     