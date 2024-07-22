from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class Gender(models.TextChoices):
    """
    Gender choices for user
    """

    MALE = "M", "Male"
    FEMALE = "F", "Female"


class Identity(models.TextChoices):
    PATIENT = "P", "Patient"
    Nurse = "D", "Nurse"
    ADMIN = "A", "Admin"


# remember to create class for user payment methods
class User(AbstractUser):
    """
    User override model for authentication.
    """

    id = models.AutoField(primary_key=True)
    national_id = models.CharField(max_length=55, unique=True)
    identity = models.CharField(max_length=8, choices=Identity)
    gender = models.CharField(max_length=8, choices=Gender)
    phone_number = models.CharField(max_length=20)
    bio = models.TextField(blank=True)
    nationality = models.CharField(max_length=100)
    location = models.CharField(max_length=55)
    city = models.CharField(max_length=55)
    country = models.CharField(max_length=55)
    date_of_birth = models.DateField()

    is_staff = None
    is_active = None
    last_login = None
    groups = None
    user_permissions = None
    # django depend on username in authentication process but
    # we want to depend on email in authentication process
    # because email is unique field
    # so we have to manually set username field to email
    USERNAME_FIELD = "email"

    class Meta:
        abstract = True


# remember to create list of diseases
class Patient(User):
    profile_image = models.ImageField(upload_to="profile_images/", blank=True, null=True)
    chronic_diseases = models.CharField(max_length=255, blank=True, null=True)
    medical_report = models.FileField(upload_to='reports/', blank=True, null=True)

    def __str__(self):
        return self.name


class Nurse(User):
    profile_image = models.ImageField(upload_to="profile_images/")
    specialization = models.CharField(max_length=100)
    certificates = models.FileField(upload_to='certificates/')
    medical_accreditations = models.FileField(upload_to='accreditations/')
    available_working_hours = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Admin(User):
    profile_image = models.ImageField(upload_to="profile_images/")

    def __str__(self):
        return self.name


class AbstractSession(models.Model):
    id = models.AutoField(primary_key=True)
    session_type = models.CharField(max_length=55)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Session(AbstractSession):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='sessions')
    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE, related_name='sessions')
    paid_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_sessions = models.PositiveIntegerField()
    remaining_sessions = models.PositiveIntegerField()
    prev_session = models.OneToOneField("self", on_delete=models.CASCADE, related_name='prev', null=True)
    next_session = models.OneToOneField("self", on_delete=models.CASCADE, related_name='next', null=True)
    place = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"Session between {self.patient.name} and {self.nurse.name}"
