from django.db.models import F
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import HasModulePermission
from .models import Supplier, InventoryItem, InventoryTransaction
from .serializers import (
    SupplierSerializer, InventoryItemSerializer, InventoryTransactionSerializer,
)


class SupplierViewSet(viewsets.ModelViewSet):
    module = "inventory"
    permission_classes = [HasModulePermission]
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    search_fields = ["name", "phone"]


class InventoryItemViewSet(viewsets.ModelViewSet):
    module = "inventory"
    permission_classes = [HasModulePermission]
    queryset = InventoryItem.objects.select_related("supplier")
    serializer_class = InventoryItemSerializer
    search_fields = ["name", "category"]
    filterset_fields = ["category", "supplier"]

    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request):
        qs = self.get_queryset().filter(quantity__lte=F("minimum_stock"))
        return Response(self.get_serializer(qs, many=True).data)


class InventoryTransactionViewSet(viewsets.ModelViewSet):
    module = "inventory"
    permission_classes = [HasModulePermission]
    queryset = InventoryTransaction.objects.select_related("item", "supplier")
    serializer_class = InventoryTransactionSerializer
    filterset_fields = ["item", "type", "treatment"]
    ordering_fields = ["created_at"]

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user if self.request.user.is_authenticated else None
        )
