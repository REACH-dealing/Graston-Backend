from django.contrib import admin
from .models import Nurse, Patient, Session, Admin

# Register your models here.


admin.site.register(Nurse)
admin.site.register(Patient)
admin.site.register(Session)
admin.site.register(Admin)
