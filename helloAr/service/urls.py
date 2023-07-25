from service.views import ARServiceDetail, ARServiceListCreate, ProductDetail, ProductListCreate,ListCategories,ProductHealtList
from django.urls import path




urlpatterns = [
    path("product/", ProductListCreate.as_view(), name="products"),
    path('categories/', ListCategories.as_view(), name='categories'),
    path('health/', ProductHealtList.as_view(), name='health'),
    path("product/<int:pk>/", ProductDetail.as_view(), name="product"),
    path("ar/", ARServiceListCreate.as_view(), name="arservices"),
    path("ar/<int:pk>/", ARServiceDetail.as_view(), name="arservice"),
]