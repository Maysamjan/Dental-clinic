from rest_framework.routers import DefaultRouter

from .views import (
    InvoiceViewSet, PaymentViewSet,
    InstallmentPlanViewSet, InstallmentViewSet,
)

router = DefaultRouter()
router.register("invoices", InvoiceViewSet)
router.register("payments", PaymentViewSet)
router.register("installment-plans", InstallmentPlanViewSet)
router.register("installments", InstallmentViewSet)

urlpatterns = router.urls
