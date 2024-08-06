from django.contrib import admin
from .models import User, Nurse, Patient, Admin, WorkAvailableHours


admin.site.register(User)
admin.site.register(Nurse)
admin.site.register(Patient)
admin.site.register(Admin)
admin.site.register(WorkAvailableHours)
