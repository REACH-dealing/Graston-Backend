from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import validate_email

class Gender(models.TextChoices):
    """
    Gender choices for user
    """

    MALE = "M", "Male"
    FEMALE = "F", "Female"


class Identity(models.TextChoices):
    """
    Identity choices for user
    """

    PATIENT = "P", "Patient"
    NURSE = "D", "Nurse"
    ADMIN = "A", "Admin"


# remember to create class for user payment methods
class User(AbstractUser):
    """
    User override model for authentication.
    """

    id = models.AutoField(primary_key=True)
    national_id = models.CharField(max_length=55, unique=True)
    identity = models.CharField(max_length=8, choices=Identity)
    email = models.EmailField(
        max_length=63, blank=True, null=True, validators=[validate_email], unique=True,
    )
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=8, choices=Gender, blank=True)
    nationality = models.CharField(max_length=27, blank=True)
    location = models.CharField(max_length=55, blank=True)
    city = models.CharField(max_length=27, blank=True)
    country = models.CharField(max_length=27, blank=True)
    date_of_birth = models.DateField(blank=True)
    profile_image = models.ImageField(
        upload_to="media/profile_images/", blank=True, null=True
    )
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)


    last_login = None
    groups = None
    user_permissions = None
    # django depend on username in authentication process but
    # we want to depend on email in authentication process
    # because email is unique field
    # so we have to manually set username field to email
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


# remember to create list of diseases
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    chronic_diseases = models.CharField(max_length=255, blank=True, null=True)
    medical_report = models.FileField(upload_to="reports/", blank=True, null=True)


# remember to handle working hours field
class Nurse(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    certificates = models.FileField(upload_to="certificates/", blank=True, null=True)
    medical_accreditations = models.FileField(
        upload_to="accreditations/", blank=True, null=True
    )
    available_working_hours = models.CharField(max_length=255, blank=True, null=True)


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


# class AbstractSession(models.Model):
#     id = models.AutoField(primary_key=True)
#     session_type = models.CharField(max_length=55)
#     price = models.DecimalField(max_digits=10, decimal_places=2)


# class Session(AbstractSession):
#     patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='sessions')
#     nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE, related_name='sessions')
#     paid_price = models.DecimalField(max_digits=10, decimal_places=2)
#     total_sessions = models.PositiveIntegerField()
#     remaining_sessions = models.PositiveIntegerField()
#     prev_session = models.OneToOneField("self", on_delete=models.CASCADE, related_name='prev', null=True)
#     next_session = models.OneToOneField("self", on_delete=models.CASCADE, related_name='next', null=True)
#     place = models.CharField(max_length=100)
#     start_time = models.DateTimeField()
#     end_time = models.DateTimeField()

#     def __str__(self):
#         return f"Session between {self.patient.name} and {self.nurse.name}"


class VerificationRequests(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    email = models.EmailField(
        max_length=63, blank=True, null=True, validators=[validate_email]
    )

    phone_number = models.CharField(max_length=20, blank=True, null=True)

    otp = models.SmallIntegerField(blank=True, null=True)
    otp_max_try = models.SmallIntegerField(default=3)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    otp_max_out = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)