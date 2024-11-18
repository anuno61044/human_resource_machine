from django.db import models

# Create your models here.
class Result(models.Model):
    agents = models.CharField(max_length= 10000)
    input = models.CharField(max_length= 10000)