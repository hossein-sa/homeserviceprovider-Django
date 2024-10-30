from celery import shared_task
from django.core.management import call_command


@shared_task
def expire_orders_task():
    call_command("expire_orders")