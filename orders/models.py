from django.db import models
from django.conf import settings
from services.models import SubService
from django.utils import timezone
from datetime import timedelta


class OrderStatus(models.TextChoices):
    WAITING_FOR_PROPOSALS = 'waiting_for_proposals', 'Waiting for specialist proposals'
    WAITING_FOR_SELECTION = 'waiting_for_selection', 'Waiting for specialist selection'
    WAITING_FOR_ARRIVAL = 'waiting_for_arrival', 'Waiting for specialist to arrive'
    STARTED = 'started', 'Started'
    COMPLETED = 'completed', 'Completed'
    PAID = 'paid', 'Paid'
    CANCELLED = 'cancelled', 'Cancelled'
    EXPIRED = 'expired', 'Expired'


class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    sub_service = models.ForeignKey(SubService, on_delete=models.CASCADE, related_name='orders')
    description = models.TextField()
    suggested_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
        default=OrderStatus.WAITING_FOR_PROPOSALS
    )
    scheduled_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.TextField(blank=True, null=True)
    visible_until = models.DateTimeField(default=timezone.now() + timedelta(hours=24))

    def save(self, *args, **kwargs):
        # Set visible_until based on sub-service's expiration_hours
        if not self.visible_until:
            self.visible_until = timezone.now() + timedelta(hours=self.sub_service.expiration_hours)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.username}"


class Proposal(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='proposals')
    specialist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='proposals')
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_duration = models.DurationField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proposal #{self.id} for Order #{self.order.id} by {self.specialist.username}"
