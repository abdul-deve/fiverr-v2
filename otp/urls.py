from django.urls import path, include
from otp.views import OTPViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("otp", OTPViewSet, basename="otp")

urlpatterns = [
    path("", include(router.urls)),
]
