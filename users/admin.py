from django.contrib import admin
from .models import User, Profile
from services.models import SpecialistService

# Inline Profile model for User
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

# Inline SpecialistService model for User
class SpecialistServiceInline(admin.StackedInline):
    model = SpecialistService
    can_delete = False
    verbose_name_plural = 'Specialist Service'
    fk_name = 'specialist'

# Custom UserAdmin to include Profile and SpecialistService inlines
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = (ProfileInline, SpecialistServiceInline,)
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('role', 'is_active', 'is_staff')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username', 'bio')
