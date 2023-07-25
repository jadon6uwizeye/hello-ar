from django.shortcuts import render
from rest_framework import generics

from service.models import ARService, Product,ProductCategory, ProductHealth
from service.serializers import ARServiceSerializer, ProductDetailSerializer, ProductSerializer,ProductCategorySerializer,ProductHealthSerializer
from drf_yasg.utils import swagger_auto_schema



class ListCategories(generics.ListAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

class ProductHealtList(generics.ListAPIView):
    queryset = ProductHealth.objects.filter()
    serializer_class = ProductHealthSerializer

class ProductListCreate(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    # print request body
    def perform_create(self, serializer):
        print(self.request.data)
        serializer.save()
    
    # on get use a different serializer
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductDetailSerializer
        return ProductSerializer


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

class ARServiceListCreate(generics.ListCreateAPIView):
    serializer_class = ARServiceSerializer
    queryset = ARService.objects.all()

class ARServiceDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ARServiceSerializer
    queryset = ARService.objects.all()
    
