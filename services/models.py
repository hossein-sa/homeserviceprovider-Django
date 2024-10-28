from django.db import models
from django.core.validators import MinValueValidator

class MainService(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class SubService(models.Model):
    main_service = models.ForeignKey(MainService, on_delete=models.CASCADE, related_name='sub_services')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.name} ({self.main_service.name})"