from service.views import ARServiceDetail, ARServiceListCreate, ProductDetail, ProductDetailUnauthenticated, ProductListCreate,ListCategories,ProductHealtList, record_purchase_analytics, record_view_analytics, product_analytics,create_user_plan,get_user_plan
from django.urls import path




urlpatterns = [
    path("product/", ProductListCreate.as_view(), name="products"),
    path('categories/', ListCategories.as_view(), name='categories'),
    path('health/', ProductHealtList.as_view(), name='health'),
    path("product/<str:pk>/", ProductDetail.as_view(), name="product"),
    path('product/unauthenticated/<str:pk>/', ProductDetailUnauthenticated.as_view(), name='product_unauthenticated'),
    path("product/add/view/<str:pk>", record_view_analytics, name="product_add_view"),
    path("product/add/purchase/<str:pk>", record_purchase_analytics, name="product_add_view"),
    path("product/analytiics/<str:pk>", product_analytics, name="product_analytics"),
    path("create-plan/", create_user_plan, name="create_plan"),
    path("get-plan/", get_user_plan, name="get_plan"),
]