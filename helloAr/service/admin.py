from django.contrib import admin

# Register your models here.
from .models import ARService, ProductCategory, ProductHealth, Product, ProductAnalytics
admin.site.register(ProductCategory)
admin.site.register(ProductHealth)
# on product show created at as well as updated at

admin.site.register(ARService)
admin.site.register(Product)
admin.site.register(ProductAnalytics)
