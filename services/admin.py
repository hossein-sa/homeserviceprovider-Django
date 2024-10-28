from django.contrib import admin
from .models import MainService, SubService, SpecialistService

@admin.register(MainService)
class MainServiceAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(SubService)
class SubServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_service', 'base_price')
    list_filter = ('main_service',)
    fields = ('main_service', 'name', 'description', 'base_price')

@admin.register(SpecialistService)
class SpecialistServiceAdmin(admin.ModelAdmin):
    list_display = ('specialist', 'main_service')
    list_filter = ('main_service',)
    search_fields = ('specialist__username', 'main_service__name')
    filter_horizontal = ('sub_service',)  # This should work if sub_services is correctly a ManyToManyField
