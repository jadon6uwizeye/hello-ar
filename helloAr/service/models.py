from django.db import models

# Create your models here.
class ARService(models.model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    modeling_format = models.CharField(max_length=100)
    selected_option = models.CharField(max_length=100)
    modeling_name = models.CharField(max_length=100)
    modeling_volume = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    

class Product(models.Model):
    CONDITION_CHOICES = (
        ('Serviced', 'Serviced'),
        ('UnServiced', 'UnServiced'),
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    service_period = models.CharField(max_length=100)
    product_condition = models.CharField(max_length=100, choices=CONDITION_CHOICES, default='Serviced'),
    product_list = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name