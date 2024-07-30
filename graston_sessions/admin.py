from django.contrib import admin
from .models import SessionType, Session, SessionPackage

from django.contrib.gis.db import models
from django.contrib.gis.forms import OSMWidget
# Register your models here.

class SessionModelAdmin(admin.ModelAdmin):
    formfield_overrides = {models.PointField: {"widget": OSMWidget}}

admin.site.register(SessionType)
admin.site.register(Session, SessionModelAdmin)
admin.site.register(SessionPackage)









