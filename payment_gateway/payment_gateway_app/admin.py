from django.contrib import admin
from payment_gateway_app.models import product, payment_detail

# Register your models here.
admin.site.register(product) # register product model
admin.site.register(payment_detail) # register payment_detail model
