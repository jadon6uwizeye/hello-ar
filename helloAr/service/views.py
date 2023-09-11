from datetime import date
from django.shortcuts import render
from rest_framework import generics

from service.models import ARService, Product, ProductAnalytics,ProductCategory, ProductHealth, UserPlan
from service.serializers import ARServiceSerializer, ProductDetailSerializer, ProductSerializer,ProductCategorySerializer,ProductHealthSerializer, ProductsUpdateSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework import serializers
from django.db.models import Count, Sum
from rest_framework.pagination import PageNumberPagination

from django.db.models import Sum, Min, Max, F, FloatField,Value
from datetime import datetime, timedelta
from django.db.models.functions import Cast,Coalesce



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

        # Date range filter
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')

        if date_from and date_to:
            product_analytics_queryset = product_analytics_queryset.filter(date__range=(date_from, date_to))
        
        # Last day, last week, last month filter
        date_filter = request.GET.get('date_filter')
        today = datetime.now().date()

        if date_filter == 'last_day':
            product_analytics_queryset = product_analytics_queryset.filter(date=today)
        elif date_filter == 'last_week':
            last_week = today - timedelta(days=7)
            product_analytics_queryset = product_analytics_queryset.filter(date__range=(last_week, today))
        elif date_filter == 'last_month':
            last_month = today - timedelta(days=30)
            product_analytics_queryset = product_analytics_queryset.filter(date__range=(last_month, today))

        # Category filter
        category = request.GET.get('category')

        if category:
            product_analytics_queryset = product_analytics_queryset.filter(category=category)

        # get the total views and purchases for each date
        total_visitors = product_analytics_queryset.values("date").annotate(total_visitors=Sum("views"))
        new_visitors = product_analytics_queryset.values("date").annotate(new_visitors=Sum("purchases"))
        # get the total rate for each date as a fraction of total purchases and total views
        purchase_rate = product_analytics_queryset.values("date").annotate(purchase_rate=
                                                                        Cast(Coalesce(Sum("purchases"), Value(0)), FloatField())/Cast(Coalesce(Sum("views"), Value(1)), FloatField()) * 100)

        # Combine the data into the desired format
        analytics = []
        for i in range(len(total_visitors)):
            date = total_visitors[i]["date"]
            views = total_visitors[i]["total_visitors"]
            purchases = new_visitors[i]["new_visitors"]
            rate = purchase_rate[i]["purchase_rate"]

            # Append data to the analytics list in the specified format
            analytics.append({"date": date, "value": views, "category": "total_visitors"})
            analytics.append({"date": date, "value": purchases, "category": "new_visitors"})
            analytics.append({"date": date, "value": rate, "category": "purchase_rate"})

        return Response(
            status=status.HTTP_200_OK,
            data={
                "total_views": product_analytics_queryset.aggregate(total_visitors=Sum("views"))['total_visitors'],
                "total_purchases": product_analytics_queryset.aggregate(new_visitors=Sum("purchases"))['new_visitors'],
                "total_rate": product_analytics_queryset.aggregate(purchase_rate=Cast(Coalesce(Sum("purchases"), Value((0))), FloatField())/Cast(Coalesce(Sum("views"), Value(1)), FloatField()))['purchase_rate'] * 100,
                "analytics": analytics
            }
        )
   except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)}
        )



# @api_view(['GET'])
# def product_analytics(request, pk):
    #  try:
    #     product = Product.objects.get(pk=pk)
    #     # response to return as json of analytics product views, purchases, rate and date for each date, total views, total purchases, total rate for each date
    #     product_analytics = []
    #     # get the product analytics for the product
    #     product_analytics_queryset = ProductAnalytics.objects.filter(product=product)
    #     # get the total views and purchases for each date
    #     total_visitors = product_analytics_queryset.values("date").annotate(total_visitors=Sum("views"))
    #     new_visitors = product_analytics_queryset.values("date").annotate(new_visitors=Sum("purchases"))
    #     # get the total rate for each date as a fraction of total purchases and total views
    #     purchase_rate = product_analytics_queryset.values("date").annotate(purchase_rate=Sum("purchases")/Sum("views"))

    #     # Combine the data into the desired format
    #     analytics = []
    #     for i in range(len(total_visitors)):
    #         date = total_visitors[i]["date"]
    #         views = total_visitors[i]["total_visitors"]
    #         purchases = new_visitors[i]["new_visitors"]
    #         rate = purchase_rate[i]["purchase_rate"]

    #         # Append data to the analytics list in the specified format
    #         analytics.append({"date": date, "value": views, "category": "total_visitors"})
    #         analytics.append({"date": date, "value": purchases, "category": "new_visitors"})
    #         analytics.append({"date": date, "value": rate, "category": "purchase_rate"})

    #     return Response(
    #         status=status.HTTP_200_OK,
    #         data={
    #             "total_visitors": product_analytics_queryset.aggregate(total_visitors=Sum("views"))['total_visitors'],
    #             "new_visitors": product_analytics_queryset.aggregate(new_visitors=Sum("purchases"))['new_visitors'],
    #             "purchase_rate": product_analytics_queryset.aggregate(purchase_rate=Sum("purchases")/Sum("views"))['purchase_rate'],
    #             "analytics": analytics
    #         }
    #     )
    # except Exception as e:
    #     return Response(
    #         status=status.HTTP_400_BAD_REQUEST,
    #         data={"error": str(e)}
    #     )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user_plan(request):
    try:
        try:
            user_plan = UserPlan.objects.get(user=request.user)
            user_plan.plan_id = request.data.get('plan_id')
            user_plan.save()
            return Response(
                status=status.HTTP_200_OK,
                data={"message": "User plan updated"}
            )
        except UserPlan.DoesNotExist:
            # if user plan does not exist create it
            user_plan = UserPlan.objects.create(
                user=request.user,
                plan_id=request.data.get('plan_id')
            )
            return Response(
                status=status.HTTP_200_OK,
                data={"message": "User plan created"}
            )
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)}
        )
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_plan(request):
    try:
        try:
            user_plan = UserPlan.objects.get(user=request.user)
            return Response(
                status=status.HTTP_200_OK,
                data={"plan_id": user_plan.plan_id}
            )
        except UserPlan.DoesNotExist:
            return Response(
                status=status.HTTP_200_OK,
                data={"plan_id": None}
            )
    except Exception as e:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error": str(e)}
        )