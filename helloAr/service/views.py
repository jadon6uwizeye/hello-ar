from django.shortcuts import render
from rest_framework import generics

from service.models import ARService, Product
from service.serializers import ARServiceSerializer, ProductSerializer
# Create your views here.

class ProductListCreate(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

class ARServiceListCreate(generics.ListCreateAPIView):
    serializer_class = ARServiceSerializer
    queryset = ARService.objects.all()

class ARServiceDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ARServiceSerializer
    queryset = ARService.objects.all()
    