from rest_framework.routers import DefaultRouter

from .views import FollowUpViewSet

router = DefaultRouter()
router.register("follow-ups", FollowUpViewSet)

urlpatterns = router.urls
