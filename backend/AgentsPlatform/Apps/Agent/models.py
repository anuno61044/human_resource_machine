from django.db import models
from Apps.Functionality.models import Functionality

# Create your models here.
class Agent(models.Model):
    name = models.CharField(max_length=50)
    pythonCode = models.CharField(max_length=10000)
    function = models.ManyToManyField(Functionality)
    _type = models.BooleanField(default=True)