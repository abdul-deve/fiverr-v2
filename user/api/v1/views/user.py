from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework.exceptions import ValidationError

from django.db import transaction
from django.contrib.auth.password_validation import validate_password

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken

from user.models import User
from user.api.v1.serializer.user import (
    UserSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    VerifyANDPasswordResetSerializer,
)

from lib.email import send_otp_email,send_password_changed_email
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed


def get_tokens_for_user(user):
    if not user.is_active:
        raise AuthenticationFailed("User is not active")

    refresh = RefreshToken.for_user(user)

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


class UserViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = []

    def create(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response(
            {"user": serializer.data, "tokens": tokens}, status=status.HTTP_201_CREATED
        )

    def retrieve(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)

    def update(self, request):
        serializer = self.serializer_class(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request):
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request):
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    @action(
        detail=False,
        methods=["patch"],
        url_name="change_password",
        url_path="change_password",
        authentication_classes=[JWTAuthentication],
        permission_classes=[permissions.IsAuthenticated],
    )
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_pass = serializer.validated_data["old_password"]
        new_pass = serializer.validated_data["new_password"]

        if not user.check_password(old_pass):
            return Response(
                {"message": "Invalid current password"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            self._change_password(user, new_pass)
        except ValidationError as e:
            return Response(
                {"message": e},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK,
        )
    @staticmethod
    def _change_password(user, new_pass):
        validate_password(new_pass, user=user)

        with transaction.atomic():
            user.set_password(new_pass)
            user.save()

            tokens = OutstandingToken.objects.filter(user=user)
            BlacklistedToken.objects.bulk_create(
                [BlacklistedToken(token=t) for t in tokens],
                ignore_conflicts=True,
            )

            transaction.on_commit(
                lambda: send_password_changed_email(user)
            )

    @action(
        methods=["post"],
        url_name="request_reset_password",
        url_path="request_reset_password",
        detail=False,
    )
    def request_reset_password(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if user:
            from otp.service import PasswordResetService
            service = PasswordResetService(user=user)
            otp = service.send_otp()
            send_otp_email(user=user, otp=otp)
        return Response(
            {
                "message": (
                    "If this email address is registered with us, "
                    "you will receive an OTP to reset your password."
                )
            },
            status=status.HTTP_200_OK
        )
    @action(detail=False,methods=["post"], url_name="reset_password", url_path="reset_password")
    def check_and_reset_password(self,request):
        from otp.service import OTPService
        serializer = VerifyANDPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()
        otp = serializer.validated_data["otp"]
        password = serializer.validated_data["new_password"]
        otp_service = OTPService(user=user)
        if otp_service.verify_otp(otp):
            self._change_password(user=user,new_pass=password)
            otp_service.reset()
            return Response(
            {"message": "Password Reset Successfully"}, status=status.HTTP_200_OK
                )
        return Response(
            {"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
        )