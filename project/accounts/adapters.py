from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.shortcuts import redirect

from .models import UBU_EMAIL_DOMAIN, UbuUser
from .services import link_sso_user


class UBUSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    UC-15 ช่องทางที่ 1: เข้าสู่ระบบผ่าน UBU SSO (Google @ubu.ac.th) เท่านั้น
    - ปฏิเสธอีเมลที่ไม่ใช่ @ubu.ac.th
    - ปฏิเสธบัญชีที่ถูกระงับสิทธิ์
    - login ครั้งแรก → สร้าง USER + STUDENT
    """

    def _reject(self, request, message):
        messages.error(request, message)
        raise ImmediateHttpResponse(redirect("accounts:login"))

    def pre_social_login(self, request, sociallogin):
        email = (sociallogin.user.email or "").lower()
        if not email.endswith(f"@{UBU_EMAIL_DOMAIN}"):
            self._reject(request, f"ระบบอนุญาตให้เข้าใช้งานด้วยอีเมลมหาวิทยาลัย (@{UBU_EMAIL_DOMAIN}) เท่านั้น")
        ubu_user = UbuUser.objects.filter(email=email).first()
        if ubu_user and ubu_user.blocked:
            reason = f" เหตุผล: {ubu_user.block_reason}" if ubu_user.block_reason else ""
            self._reject(request, f"บัญชีนี้ถูกระงับสิทธิ์การใช้งาน{reason}")

    def is_open_for_signup(self, request, sociallogin):
        email = (sociallogin.user.email or "").lower()
        return email.endswith(f"@{UBU_EMAIL_DOMAIN}")

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.set_unusable_password()  # UC-15 กฎข้อ 1: ไม่เก็บรหัสผ่านของผู้ใช้ SSO
        user.save(update_fields=["password"])
        link_sso_user(user, name=user.get_full_name(), email=user.email)
        return user
