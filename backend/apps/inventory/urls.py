from rest_framework.routers import DefaultRouter

from .views import (
    SupplierViewSet, InventoryItemViewSet, InventoryTransactionViewSet,
)

router = DefaultRouter()
router.register("suppliers", SupplierViewSet)
router.register("inventory-items", InventoryItemViewSet)
router.register("inventory-transactions", InventoryTransactionViewSet)

urlpatterns = router.urls
