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
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


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
        if self.user.role == 'specialist' and not self.profile_picture:
            raise ValidationError("Profile picture is required for specialists.")

    def save(self, *args, **kwargs):
        self.clean()
        if self.user.role == 'specialist' and self.profile_picture:
            img = Image.open(self.profile_picture)
            if img.width != img.height:
                raise ValidationError("Profile picture must be a 1:1 aspect ratio.")
            if self.profile_picture.size > 400 * 1024:
                raise ValidationError("Profile picture must be under 400 KB.")
        super().save(*args, **kwargs)
