from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib import messages

ALLOWED_EMAIL_DOMAIN = "ubu.ac.th"


class UBUSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    บังคับให้ล็อกอินผ่าน Google (UBU SSO) ได้เฉพาะอีเมล @ubu.ac.th เท่านั้น
    ตาม business rule: Login ต้องเป็น UBU SSO เท่านั้น ห้ามมี Google OAuth
    แบบเปิดกว้างให้ทุกโดเมน และห้ามมีระบบ whitelist อัปโหลดรายชื่อล่วงหน้า
    """

    def pre_social_login(self, request, sociallogin):
        email = (sociallogin.user.email or "").lower()
        if not email.endswith(f"@{ALLOWED_EMAIL_DOMAIN}"):
            messages.error(
                request,
                f"ระบบอนุญาตให้เข้าใช้งานด้วยอีเมลมหาวิทยาลัย (@{ALLOWED_EMAIL_DOMAIN}) เท่านั้น"
            )
            raise ImmediateHttpResponse(redirect("accounts:login"))

    def is_open_for_signup(self, request, sociallogin):
        email = (sociallogin.user.email or "").lower()
        return email.endswith(f"@{ALLOWED_EMAIL_DOMAIN}")
