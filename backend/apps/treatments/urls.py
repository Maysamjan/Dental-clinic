from rest_framework.routers import DefaultRouter

from .views import (
    TreatmentCatalogViewSet, TreatmentPlanViewSet,
    TreatmentStageViewSet, TreatmentViewSet,
)

router = DefaultRouter()
router.register("treatment-catalog", TreatmentCatalogViewSet)
router.register("treatment-plans", TreatmentPlanViewSet)
router.register("treatment-stages", TreatmentStageViewSet)
router.register("treatments", TreatmentViewSet)

urlpatterns = router.urls
