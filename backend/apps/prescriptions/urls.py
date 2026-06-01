from rest_framework.routers import DefaultRouter

from .views import PrescriptionViewSet, PrescriptionTemplateViewSet

router = DefaultRouter()
router.register("prescription-templates", PrescriptionTemplateViewSet)
router.register("prescriptions", PrescriptionViewSet)

urlpatterns = router.urls
