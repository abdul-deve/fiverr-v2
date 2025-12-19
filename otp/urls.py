from otp.views import  OTPViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("otp",OTPViewSet,basename="otp")


