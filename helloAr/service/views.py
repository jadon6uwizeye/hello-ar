from datetime import date
from django.shortcuts import render
from rest_framework import generics

from service.models import ARService, Product, ProductAnalytics,ProductCategory, ProductHealth
from service.serializers import ARServiceSerializer, ProductAnalyticsSerializer, ProductDetailSerializer, ProductSerializer,ProductCategorySerializer,ProductHealthSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes



class ListCategories(generics.ListAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

class ProductHealtList(generics.ListAPIView):
    queryset = ProductHealth.objects.filter()
    serializer_class = ProductHealthSerializer

class ProductListCreate(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]

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
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]

# one product detail for unauthenticated users
class ProductDetailUnauthenticated(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()
    permission_classes = [AllowAny]

class ARServiceListCreate(generics.ListCreateAPIView):
    serializer_class = ARServiceSerializer
    queryset = ARService.objects.all()

class ARServiceDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ARServiceSerializer
    queryset = ARService.objects.all()
    
@api_view(['POST'])
# remove authentication here
@permission_classes([AllowAny])
def record_view_analytics(request, pk):
    product = Product.objects.get(pk=pk)
    product_analytics = ProductAnalytics.objects.get_or_create(product=product, date=date.today())[0]
    product_analytics.views += 1
    product_analytics.save()
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
# remove authentication here
@permission_classes([AllowAny])
def record_purchase_analytics(request, pk):
    product = Product.objects.get(pk=pk)
    product_analytics = ProductAnalytics.objects.get_or_create(product=product, date=date.today())[0]
    product_analytics.purchases += 1
    product_analytics.save()
    return Response(status=status.HTTP_200_OK)

# List detailed product analytics
class ProductAnalyticsList(generics.ListAPIView):
    serializer_class = ProductAnalyticsSerializer
    queryset = ProductAnalytics.objects.all()
    permission_classes = [AllowAny,]

    def get_queryset(self):
        queryset = ProductAnalytics.objects.filter(product=self.kwargs["pk"])
        return queryset