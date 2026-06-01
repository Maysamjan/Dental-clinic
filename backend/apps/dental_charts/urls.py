from rest_framework.routers import DefaultRouter

from .views import DentalChartViewSet, ToothViewSet, ToothConditionViewSet

router = DefaultRouter()
router.register("dental-charts", DentalChartViewSet)
router.register("teeth", ToothViewSet)
router.register("tooth-conditions", ToothConditionViewSet)

urlpatterns = router.urls
