from pyexpat import model
from rest_framework import serializers
from .models import product

class productSerializer(serializers.ModelSerializer):  # product detail serializer
    class Meta:
        model = product
        fields = '__all__'