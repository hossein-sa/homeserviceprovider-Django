from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import FileExtensionValidator
from PIL import Image


class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('specialist', 'Specialist'),
        ('admin', 'Admin'),
    )

    STATUS_CHOICES = (
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('inactive', 'Inactive'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')

    @property
    def is_specialist(self):
        return self.role == 'specialist'

    @property
    def is_customer(self):
        return self.role == 'customer'

    @property
    def has_wallet(self):
        return hasattr(self, 'wallet')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])],
        blank=True,
        null=True
    )
    bio = models.TextField(blank=True, null=True)

    def clean(self):
        if self.user.is_specialist and not self.profile_picture:
            raise ValidationError('Specialists must have a profile picture.')
        if self.profile_picture:
            img = Image.open(self.profile_picture)
            if img.width != img.height:
                raise ValidationError("Profile picture must have a 1:1 aspect ratio.")
            if self.profile_picture.size > 400 * 1024:
                raise ValidationError("Profile picture must be under 400 KB.")


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.user.username}'s Wallet - Balance: {self.balance}"


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"Transaction for {self.wallet.user.username} - Amount: {self.amount} on {self.timestamp}"
