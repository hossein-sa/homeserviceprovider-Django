# orders/utils.py
from decimal import Decimal

from django.db import transaction

from users.models import Transaction

ADMIN_COMMISSION_RATE = Decimal("0.30")
SPECIALIST_SHARE_RATE = Decimal("0.70")

def process_payment(customer, specialist, order_amount):
    with transaction.atomic():
        customer_wallet = customer.wallet
        specialist_wallet = specialist.wallet

        # Check if customer has enough balance
        if customer_wallet.balance < order_amount:
            raise ValueError("Insufficient balance in customer's wallet")

        # Calculate shares
        admin_share = order_amount * ADMIN_COMMISSION_RATE
        specialist_share = order_amount * SPECIALIST_SHARE_RATE

        # Deduct from customer's wallet
        customer_wallet.balance -= order_amount
        customer_wallet.save()

        # Credit to specialist's wallet
        specialist_wallet.balance += specialist_share
        specialist_wallet.save()

        # Record transactions
        Transaction.objects.create(wallet=customer_wallet, amount=-order_amount, description="Payment for service")
        Transaction.objects.create(wallet=specialist_wallet, amount=specialist_share, description="Earnings from service")
        # Admin's commission could be recorded separately if needed.
