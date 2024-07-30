from django.db import models
from django.contrib.gis.db import models as gis_models  # Assuming you are using GeoDjango for PointField

class SessionType(models.Model):
    name = models.CharField(max_length=50)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class SessionPackage(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    nurse = models.ForeignKey('Nurse', on_delete=models.CASCADE)
    session_type = models.ForeignKey(SessionType, on_delete=models.CASCADE)  # Add session type
    package_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Add package price
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Add discount price

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
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    nurse = models.ForeignKey('Nurse', on_delete=models.CASCADE)
    package = models.ForeignKey(SessionPackage, on_delete=models.SET_NULL, null=True, blank=True)
    session_type = models.ForeignKey(SessionType, on_delete=models.CASCADE)  # Add session type
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    location = gis_models.PointField()

    session_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Add session price

    status = models.CharField(max_length=20, choices=[
        ('booked', 'Booked'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
