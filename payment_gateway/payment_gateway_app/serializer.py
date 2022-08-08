from rest_framework import serializers
from .models import product, paymentDetail

class productSerializer(serializers.ModelSerializer):  # product detail serializer
    class Meta:
        model = product
        fields = '__all__'

class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = paymentDetail
        fields = '__all__'