from rest_framework.routers import DefaultRouter

from .views import ExpenseViewSet, ExpenseCategoryViewSet

router = DefaultRouter()
router.register("expense-categories", ExpenseCategoryViewSet)
router.register("expenses", ExpenseViewSet)

urlpatterns = router.urls
