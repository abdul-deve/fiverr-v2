from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from lib.models import TimeStamp

class UserManager(BaseUserManager):
    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            return ValueError("Invalid Credentials")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self._create_user(email, password, **extra_fields)


class User(TimeStamp,AbstractUser):
    username = None
    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField(max_length=255)
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        abstract = False
    def send_otp(self):
        from lib.email import send_otp_email
        send_otp_email(user=self)

class UserProfile(TimeStamp):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.OneToOneField(
        "Address", on_delete=models.CASCADE, related_name="address"
    )
    dob = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=(("male", "Male"), ("female", "Female"), ("other", "Other")),
    )
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures", null=True, blank=True
    )

    class Meta:
        abstract = False

class Address(TimeStamp):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="address")
    country = models.CharField(max_length=255, db_index=True)
    state = models.CharField(max_length=255, db_index=True)
    city = models.CharField(max_length=255, db_index=True)
    street = models.CharField(max_length=255, db_index=True)
    zip_code = models.CharField(max_length=255, db_index=True)

    class Meta:
        abstract = False


class Verification(TimeStamp):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="verification"
    )
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)

    class Meta:
        abstract = False
