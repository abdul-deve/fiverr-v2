from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.timezone import now
from otp import service

OTP_EXPIRY = getattr(settings, "OTP_EXPIRY", 300)


def get_ready_to_send_otp(user):
    otp_service = service.OTPService(user)
    otp = otp_service.generate_otp()
    return otp

def send_otp_email(user,otp=None):
    if not otp:
        otp = get_ready_to_send_otp(user)
    subject = "Your OTP code"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [user.email]

    html_content = render_to_string(
        "emails/otp.html",
        {
            "otp": otp,
            "user_name": user.get_full_name() or user.email,
            "expiry_minutes": OTP_EXPIRY // 60,
            "year": now().year,
        },
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body="Your OTP is {}".format(otp),
        from_email=from_email,
        to=to_email,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)

def send_password_changed_email(user):
    user_email = user.email
    user_name = user.get_full_name() or user.email
    support_url = ("https://support.abdul's enterprise .com")
    subject = "Your Password Has Been Changed"
    from_email = "Abdul's Enterprise <noreply@yourcompany.com>"
    to_email = user_email

    html_content = render_to_string(
        "emails/change_passwrod.html",
        {
            "user_name": user_name,
            "user_email": user_email,
            "support_url": support_url
        }
    )

    msg = EmailMultiAlternatives(subject, "", from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()