from unicodedata import name
from django.db import models

# Create your models here.
class product(models.Model):
    name = models.CharField(max_length=255, blank=False)
    description  = models.TextField(max_length=2555, blank=False)
    price = models.IntegerField(blank=False)

    def __str__(self):
        return self.name + ' ' + str(self.price)

