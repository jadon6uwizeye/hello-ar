from datetime import date
from django.shortcuts import render
from rest_framework import generics

from service.models import ARService, Product, ProductAnalytics,ProductCategory, ProductHealth
from service.serializers import ARServiceSerializer, ProductDetailSerializer, ProductSerializer,ProductCategorySerializer,ProductHealthSerializer, ProductsUpdateSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework import serializers
from django.db.models import Count, Sum
from rest_framework.pagination import PageNumberPagination



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
    pagination_class = PageNumberPagination

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

    # if update use different serializer
    # def get_serializer_class(self):
    #     if self.request.method == 'PUT' or self.request.method == 'PATCH':
    #         return ProductsUpdateSerializer
    #     return ProductDetailSerializer

    # on put remove associated arservices whcih ar not sent in products array
    def perform_update(self, serializer):
        try:
        # if it is patch request then partial update as usual
            if self.request.method == 'PATCH':
                serializer.save()
            
            # first get the product instance
            product = Product.objects.get(pk=self.kwargs["pk"])
            # get the arservices sent in the request from formdata

            print(self.request.data)

            arservices = self.request.data["products"]
            # get the arservices associated with the product
            # get the arservices as arservice instances from arservices.id
            arservices = [ARService.objects.get(pk=arservice["id"]) for arservice in arservices]
            product_arservices = product.arservice.all()
            # get the arservices to remove as the difference between the two sets
            arservices_to_remove = set(product_arservices).difference(set(arservices))
            print(arservices_to_remove)
            # remove the arservices
            product.arservice.remove(*arservices_to_remove)
            # save the product
            product.save()
            # save the serializer
            serializer.save()
        except Exception as e:
            # return error if any exception occurs
            raise serializers.ValidationError({"error": str(e)})
        


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
    try:
        product = Product.objects.get(pk=pk)
        product_analytics = ProductAnalytics.objects.create(product=product, date=date.today())
        product_analytics.views += 1
        product_analytics.save()
        return Response(
            status=status.HTTP_200_OK,
            data={"message": "View recorded"}
        )
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)}
        )

@api_view(['POST'])
# remove authentication here
@permission_classes([AllowAny])
def record_purchase_analytics(request, pk):
    try : 
        product = Product.objects.get(pk=pk)
        product_analytics = ProductAnalytics.objects.create(product=product, date=date.today())
        product_analytics.purchases += 1
        product_analytics.save()
        return Response(status=status.HTTP_200_OK,
                    data={"message": "Purchase recorded"})
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)}
        )

@api_view(['GET'])
def product_analytics(request,pk):
    try:
        product = Product.objects.get(pk=pk)
        # response to return as json of analytics product views, purchases, rate and date for each date, total views, total purchases, total rate for each date
        product_analytics = []
        # get the product analytics for the product
        product_analytics_queryset = ProductAnalytics.objects.filter(product=product)
        # get the total views and purchases for each date
        total_views = product_analytics_queryset.values("date").annotate(total_views=Sum("views"))
        total_purchases = product_analytics_queryset.values("date").annotate(total_purchases=Sum("purchases"))
        # get the total rate for each date as a fraction of total purchases and total views
        total_rate = product_analytics_queryset.values("date").annotate(total_rate=Sum("purchases")/Sum("views"))
        # get the total views, purchases and rate for each date
        for i in range(len(total_views)):
            product_analytics.append({
                "date": total_views[i]["date"],
                "views": total_views[i]["total_views"],
                "purchases": total_purchases[i]["total_purchases"],
                "rate": total_rate[i]["total_rate"]
            })

        return Response(
            status=status.HTTP_200_OK,
            data={
                "total_views": product_analytics_queryset.aggregate(total_views=Sum("views"))['total_views'],
                "total_purchases": product_analytics_queryset.aggregate(total_purchases=Sum("purchases"))['total_purchases'],
                "total_rate": product_analytics_queryset.aggregate(total_rate=Sum("purchases")/Sum("views"))['total_rate'],
                "analytics": product_analytics
                }
        )
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)}
        )
