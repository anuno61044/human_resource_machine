from django.db import models

# Create your models here.
class Functionality(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    belongs = models.CharField(max_length=5, default="1")
    
    def __str__(self):
        return self.name
