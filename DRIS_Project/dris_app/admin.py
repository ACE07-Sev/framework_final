# Name: Amir Ali Malekani Nezhad
# Student ID: S2009460

from django.contrib import admin  # type: ignore
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # type: ignore


from .models import (
    AidRequest,
    DisasterReport,
    Shelter,
    Skill,
    User,
    VolunteerAssignment,
    VolunteerInfo
)


class CustomUserAdmin(BaseUserAdmin):
    def get_form(self, request, obj=None, **kwargs): # type: ignore
        form = super().get_form(request, obj, **kwargs)
        # If the current user is not a superuser:
        if not request.user.is_superuser:
            # Lock down these critical fields
            for field in ("is_superuser", "groups", "user_permissions"):
                if field in form.base_fields: # type: ignore
                    form.base_fields[field].disabled = True # type: ignore
            # Additionally, prevent editing self-privileges
            if obj is not None and obj == request.user:
                for field in ("is_staff",):
                    if field in form.base_fields: # type: ignore
                        form.base_fields[field].disabled = True # type: ignore
        return form

# Replace default admin with this one
admin.site.register(User, CustomUserAdmin)
admin.site.register(DisasterReport)
admin.site.register(AidRequest)
admin.site.register(Shelter)
admin.site.register(VolunteerAssignment)
admin.site.register(Skill)
admin.site.register(VolunteerInfo)