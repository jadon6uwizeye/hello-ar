from django.db import models

# Create your models here.

# user model
class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=100)
    membership_info =  models.CharField(max_length=200)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    

