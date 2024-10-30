from django.core.management.base import BaseCommand
from django.utils import timezone
from orders.models import Order


class Command(BaseCommand):
    help = "Expire orders with no proposals after the visible_until time has passed."

    def handle(self, *args, **kwargs):
        # Get the current time
        now = timezone.now()

        # Find orders past their visible_until time with no proposals and status 'waiting_for_proposals'
        expired_orders = Order.objects.filter(
            visible_until__lte=now,
            status='waiting_for_proposals',
            proposals__isnull=True  # Ensures no proposals were submitted
        )

        # Update the status of each order to 'expired'
        count = expired_orders.update(status='expired')
        self.stdout.write(f"Expired {count} orders due to lack of proposals.")
