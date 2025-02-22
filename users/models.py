from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    phone = models.CharField(max_length=25, blank=True, null=True, verbose_name="Phone number")
    data_birth = models.DateTimeField(blank=True, null=True, verbose_name='Date of birth')