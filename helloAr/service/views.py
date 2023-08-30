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

from django.db.models import Sum, Min, Max
from datetime import timedelta



class ListCategories(generics.ListAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

class ProductHealtList(generics.ListAPIView):
    queryset = ProductHealth.objects.filter()
    serializer_class = ProductHealthSerializer

class ProductListCreate(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all().order_by('-updated_at')
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

   
    
    # on get use a different serializer
    def get_serializer_class(self):
        if self.request.method == 'GET':
            print("get")
            return ProductDetailSerializer
        else:
            # get update query param if it exists
            update = self.request.query_params.get('update')
            print("update")
            print(update)
            
            # if the requst has update param in request first delete the existing product
            if update != None:
                print("update")
                if self.request.method == 'POST':
                    try:
                        print("delete")
                        product = Product.objects.get(pk=self.request.data.get('id'))
                        print(product)
                        
                        # delete associated arservices
                        product_ar_services = product.arservice.filter(
                            products=product
                        )

                        # delete product but before remove arservices association
                        product.arservice.remove(*product_ar_services)
                        product.delete()
                        print("deleted")
                        print(product_ar_services)

                        print("check here")

                        print("here")
                        print(product_ar_services)
                        print("here")
                        # return ProductSerializer and pass context
                        ProductSerializer.context= {'product_ar_services': product_ar_services,
                                                    'request': self.request}
                        
                        return ProductSerializer
                    except Product.DoesNotExist:
                        # raise a 404 exception if product does not exist
                        raise serializers.ValidationError(
                            {"error": "Product(Id given) on update does not exist"}
                    )
            ProductSerializer.context= {'request': self.request}
            return ProductSerializer
        
    def get_queryset(self):
        queryset = Product.objects.all().order_by('-updated_at').filter(
            created_by=self.request.user
        )
        return queryset


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]

    # # if update use different serializer
    # def get_serializer_class(self):
    #     if self.request.method == 'PUT' or self.request.method == 'PATCH':
    #         # return ProductsUpdateSerializer passing request data
    #         return ProductsUpdateSerializer
    #     return ProductDetailSerializer
    
    def perform_update(self, serializer):
        product = self.get_object()
        # Get the list of ARService IDs from the update request
        updated_arservices_ids = [arservice['id'] for arservice in self.request.data.get('products', [])]
        print("updated_arservices_ids ", updated_arservices_ids)

        # Get the list of ARServices associated with the product
        existing_arservices = product.arservice.all()

        for arservice in existing_arservices:
            print("arservice.id ", arservice.id)
            if str(arservice.id) not in updated_arservices_ids:
                print("here")
                print("arservice.id ", arservice.id)
                product.arservice.remove(arservice)
                print("removed")       

        # Find the ARServices that need to be removed
        # arservices_to_remove = [arservice for arservice in existing_arservices if arservice.id not in updated_arservices_ids]
        arservices_to_remove = []
        print("arservices_to_remove ", arservices_to_remove)

        # Remove the ARServices that need to be removed
        for arservice in arservices_to_remove:
            product.arservice.remove(arservice)

        # Save the updated product
        serializer.save()



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


# @api_view(['GET'])
# def product_analytics(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        # response to return as JSON of analytics for date ranges: views, purchases, rate and date range
        product_analytics = []
        # get the product analytics for the product
        product_analytics_queryset = ProductAnalytics.objects.filter(product=product)

        # Calculate the date range boundaries
        min_date = product_analytics_queryset.aggregate(min_date=Min("date"))['min_date']
        max_date = product_analytics_queryset.aggregate(max_date=Max("date"))['max_date']
        date_range_size = (max_date - min_date) / 5  # Divide the date range into 5 parts

        for i in range(5):
            start_date = min_date + i * date_range_size
            end_date = start_date + date_range_size

            analytics_within_range = product_analytics_queryset.filter(date__gte=start_date, date__lte=end_date)
            
            total_views = analytics_within_range.aggregate(total_views=Sum("views"))['total_views']
            total_purchases = analytics_within_range.aggregate(total_purchases=Sum("purchases"))['total_purchases']
            
            if total_views == 0:
                total_rate = 0  # Avoid division by zero
            else:
                total_rate = total_purchases / total_views

            product_analytics.append({
                "date_range": {
                    "start_date": start_date.strftime('%Y-%m-%d'),
                    "end_date": end_date.strftime('%Y-%m-%d')
                },
                "views": total_views,
                "purchases": total_purchases,
                "rate": total_rate
            })

        return Response(
            status=status.HTTP_200_OK,
            data={
                "total_views": product_analytics_queryset.aggregate(total_views=Sum("views"))['total_views'],
                "total_purchases": product_analytics_queryset.aggregate(total_purchases=Sum("purchases"))['total_purchases'],
                "total_rate": product_analytics_queryset.aggregate(total_rate=Sum("purchases") / Sum("views"))['total_rate'],
                "analytics": product_analytics
            }
        )
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)}
        )