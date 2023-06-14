from rest_framework import serializers

from service.models import ARService, Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields =  '__all__'

class ARServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ARService
        fields =  '__all__'
        