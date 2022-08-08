from django.contrib import admin
from payment_gateway_app.models import product, paymentDetail

# Register your models here.
admin.site.register(product) # register product model
admin.site.register(paymentDetail) # register payment_detail model
