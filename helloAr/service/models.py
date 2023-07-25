from datetime import timezone, datetime, date
from django.db import models

# Create your models here.
class ARService(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    model_file = models.FileField(upload_to='armodels/')
    file_size = models.FloatField(null=True, blank=True)
    file_type = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name
    
class ProductHealth(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    CONDITION_CHOICES = (
        ('Serviced', 'Serviced'),
        ('UnServiced', 'UnServiced'),
    )
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    product_condition = models.CharField(max_length=100, choices=CONDITION_CHOICES, default='Serviced'),
    category = models.CharField(max_length=100, null=True, blank=True)
    health = models.ForeignKey(ProductHealth, on_delete=models.CASCADE)
    arservice = models.ManyToManyField(ARService, related_name='products')
    product_link = models.URLField(max_length=200, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    # def __str__(self):
    #     return self.name