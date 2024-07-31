from django.db import models
from users.models import Patient, Nurse
from django.contrib.gis.db import models
# Create your models here.

class SessionType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=55)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SessionPackage(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, blank=None, null=True)
    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE, blank=None, null=True)

    session_type = models.ForeignKey(SessionType, on_delete=models.CASCADE)

    total_sessions = models.IntegerField()
    sessions_completed = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Session(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE)
    package = models.ForeignKey(SessionPackage, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    session_type = models.ForeignKey(SessionType, on_delete=models.CASCADE)  # Add session type

    location = models.PointField()

    status = models.CharField(max_length=20, choices=[
        ('booked', 'Booked'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)