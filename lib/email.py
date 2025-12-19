from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.timezone import now

def send_otp_email(user):
    """
    Generates OTP and sends it via HTML email
    """
    from otp.service import OTPService

    otp_service = OTPService(user)
    otp = otp_service.generate_otp()

    subject = "Your verification code"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [user.email]

    html_content = render_to_string(
        "email_otp.html",
        {
            "otp": otp,
            "user_name": user.get_full_name() or user.email,
            "expiry_minutes": settings.OTP_EXPIRY // 60,
            "year": now().year,
        }
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body="Your OTP is {}".format(otp),
        from_email=from_email,
        to=to_email,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)
