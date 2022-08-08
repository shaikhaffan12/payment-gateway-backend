from django.db import models

# Create your models here.
class product(models.Model): # models for product 
    name = models.CharField(max_length=255, blank=False)
    description  = models.TextField(max_length=2555, blank=False)
    price = models.IntegerField(blank=False)
    image_url = models.URLField(blank=False, null=True)

    def __str__(self):
        return self.name + ' ' + str(self.price)

class paymentDetail(models.Model): # model for payment details 
    email = models.EmailField(blank=False)
    name = models.CharField(max_length=255, blank=False)
    amount = models.IntegerField(blank=False)
    city = models.CharField(max_length=255, blank=False)
    state = models.CharField(max_length=255, blank=False)
    country = models.CharField(max_length=255, blank=False)
    status = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return self.name + ' || ' + self.email