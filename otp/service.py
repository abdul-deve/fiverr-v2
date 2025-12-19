from otp.models import OTPManager
from django.contrib.auth import get_user_model
from django.conf import settings
import pyotp
from django.utils import timezone

User = get_user_model()
Max_OTP_Attempts = getattr(settings, "Max_OTP_Attempts", 3)
OTP_Expiry = getattr(settings, "OTP_EXPIRY", 300)


class MaxOTPAttemptsExceededError(Exception):
    pass

class OTPExpiredError(Exception):
    pass


class OTPService:

    def __init__(self,user:User):
        self.manager = self.get_manager(user)


    @staticmethod
    def get_manager(user:User):
        manager ,_ = OTPManager.objects.get_or_create(user=user)
        return manager

    @staticmethod
    def generate_key():
        return pyotp.random_base32()

    def generate_otp(self):
        self.reset(commit=False)
        self.manager.last_attempt = timezone.now()
        self.manager.save(update_fields=["secret_key","last_attempt","attempts"])
        return pyotp.TOTP(self.manager.secret_key, interval=OTP_Expiry).now()

    def reset(self,commit=True):
        self.manager.secret_key = self.generate_key()
        self.manager.attempts = 0
        self.manager.last_attempt = None
        if commit:
            self.manager.save(update_fields = ["secret_key","attempts","last_attempt"])

    def verify_otp(self, otp: str):
        m = self.manager
        self.is_valid()
        totp = pyotp.TOTP(m.secret_key, interval=OTP_Expiry)
        if not totp.verify(otp):
            m.attempts += 1
            m.last_attempt = timezone.now()
            m.save(update_fields=["attempts", "last_attempt"])
            return False
        self.reset()
        return True

    def is_valid(self):
        from datetime import timedelta
        if (
                self.manager.last_attempt and
                self.manager.last_attempt + timedelta(seconds=OTP_Expiry) < timezone.now()
        ):
            raise OTPExpiredError("OTP is expired")
        if self.manager.attempts >= Max_OTP_Attempts:
            raise MaxOTPAttemptsExceededError("Too many attempts")
        return True









