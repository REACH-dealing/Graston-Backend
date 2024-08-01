from django.contrib import admin
from .models import User, Nurse, Patient, Admin

# Register your models here.


admin.site.register(User)
admin.site.register(Nurse)
admin.site.register(Patient)
admin.site.register(Admin)
