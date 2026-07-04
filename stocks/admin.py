from django.contrib import admin
from .models import Warehouse, Product
# Register your models here.


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'localisation', 'capacite')
    search_fields = ('nom', 'localisation')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'quantite', 'date_expiration', 'etat', 'entrepot')
    search_fields = ('nom', 'entrepot__nom')

