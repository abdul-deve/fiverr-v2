from rest_framework import serializers


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)


class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
