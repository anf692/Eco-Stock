from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Warehouse, Product
from .serializers import WarehouseSerializer, ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        product = self.get_object()
        new_warehouse_id = request.data.get('new_warehouse_id')

        if product.etat == 'perime':
            return Response(
                {'error': 'Impossible de déplacer un produit périmé.'},
                status=400
            )

        try:
            new_warehouse = Warehouse.objects.get(id=new_warehouse_id)
        except Warehouse.DoesNotExist:
            return Response({'error': 'Entrepôt non trouvé.'}, status=404)

        product.entrepot = new_warehouse
        product.save()
        return Response({'status': 'Produit déplacé avec succès.'})

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

    @action(detail=True, methods=['get'])
    def audit(self, request, pk=None):
        warehouse = self.get_object()
        produits = warehouse.produits

        data = {
            'entrepot': warehouse.nom,
            'total_produits': produits.count(),
            'disponible': produits.filter(etat='disponible').count(),
            'reserve': produits.filter(etat='reserve').count(),
            'perime': produits.filter(etat='perime').count(),
        }
        return Response(data)


    

    