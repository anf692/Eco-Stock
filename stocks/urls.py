from rest_framework.routers import DefaultRouter
from .views import WarehouseViewSet, ProductViewSet

router = DefaultRouter()

router.register(r'products', ProductViewSet)
router.register(r'warehouses', WarehouseViewSet)

urlpatterns = router.urls

