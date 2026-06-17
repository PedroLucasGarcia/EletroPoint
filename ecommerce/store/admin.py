from django.contrib import admin
from .models import *

# -------------------- PRODUCT ADMIN --------------------

class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "image"]
    list_filter = ["category", "brand"]
    search_fields = ["name", "category__name", "brand__name"]

admin.site.register(Product, ProductAdmin)

# -------------------- OUTROS MODELOS --------------------

admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)