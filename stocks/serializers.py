from rest_framework import serializers
from .models import Warehouse, Product


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'nom', 'localisation', 'capacite']


class ProductSerializer(serializers.ModelSerializer):
    # On ajoute un champ supplémentaire pour afficher le nom de l'entrepôt associé à chaque produit
    #StringRelatedField permet d'afficher la représentation en chaîne de caractères de l'objet lié 
    entrepot_nom = serializers.StringRelatedField(source='entrepot', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'nom', 'quantite', 'date_expiration', 'etat', 'entrepot', 'entrepot_nom']

