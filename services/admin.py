from django.contrib import admin
from .models import MainService, SubService

@admin.register(MainService)
class MainServiceAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(SubService)
class SubServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_service', 'base_price')
    list_filter = ('main_service',)
    fields = ('main_service', 'name', 'description', 'base_price')  # Customize fields in admin form
