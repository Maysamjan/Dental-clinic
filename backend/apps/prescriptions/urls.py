from rest_framework.routers import DefaultRouter

from .views import PrescriptionViewSet

router = DefaultRouter()
router.register("prescriptions", PrescriptionViewSet)

urlpatterns = router.urls
