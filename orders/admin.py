from django.contrib import admin
from .models import Order, Proposal

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'sub_service', 'status', 'scheduled_date', 'created_at')
    list_filter = ('status', 'sub_service', 'created_at')
    search_fields = ('customer__username', 'sub_service__name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'specialist', 'proposed_price', 'estimated_duration', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('order__id', 'specialist__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)