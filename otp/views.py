from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from otp.models import OTPManager
from otp.service import OTPService
from otp.serializer import (
    SendOTPSerializer,
    VerifyOTPSerializer,
)
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from lib.email import send_otp_email


User = get_user_model()

class OTPViewSet(viewsets):

    @action(methods=["post"],detail=False,url_name="send_otp",url_path= "send_otp")
    def send_otp(self,request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()
        send_otp_email(user)
        return Response({
            "message" : "OTP will be send to your email if it exists "
        })

    @action(methods=["post"],detail=False,url_name="verify_opt",url_path="verify_otp")
    def verify_otp(self,request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email =  serializer.validated_data.get("email")
        otp = serializer.validated_data.get("otp")
        user = User.obejct.filter(email=email).first()
        otp_service = OTPService(user)
        try:
            otp_service.verify_otp(otp)
            return Response({
                "message":"OTP verified successfully"
            })
        except Exception as e:
            return Response ({
                "message " : str(e),
                status : status.HTTP_400_BAD_REQUEST
            })






