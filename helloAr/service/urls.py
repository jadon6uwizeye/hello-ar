from service.views import ARServiceDetail, ARServiceListCreate, ProductDetail, ProductListCreate
from django.urls import path




urlpatterns = [
    path("product/", ProductListCreate.as_view(), name="products"),
    path("product/<int:pk>/", ProductDetail.as_view(), name="product"),
    path("ar/", ARServiceListCreate.as_view(), name="arservices"),
    path("ar/<int:pk>/", ARServiceDetail.as_view(), name="arservice"),
]