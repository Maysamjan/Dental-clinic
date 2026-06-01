from rest_framework import viewsets

from apps.core.permissions import HasModulePermission
from .models import Expense, ExpenseCategory
from .serializers import ExpenseSerializer, ExpenseCategorySerializer


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    module = "expenses"
    permission_classes = [HasModulePermission]
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    module = "expenses"
    permission_classes = [HasModulePermission]
    queryset = Expense.objects.select_related("category")
    serializer_class = ExpenseSerializer
    filterset_fields = ["category", "date"]
    search_fields = ["description"]
    ordering_fields = ["date", "amount"]

    def perform_create(self, serializer):
        serializer.save(
            recorded_by=self.request.user if self.request.user.is_authenticated else None
        )
