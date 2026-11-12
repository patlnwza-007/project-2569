from django.shortcuts import redirect
from django.urls import Resolver404, resolve, reverse

from .roles import ADMIN, STUDENT, get_role, get_ubu_user

# ไม่ต้องตรวจ: Django admin, ไฟล์ static/media, dev reload
EXEMPT_PREFIXES = ("/admin/", "/static/", "/media/", "/__reload__/")
# หน้าของ accounts ที่ผู้ใช้ทุกสถานะต้องเข้าได้ (หน้าอื่นของ accounts เช่น profile ยังถูกตรวจตามปกติ)
OPEN_ACCOUNT_PAGES = {"login", "logout", "blocked", "onboarding"}


def is_exempt(path):
    if path.startswith(EXEMPT_PREFIXES):
        return True
    try:
        match = resolve(path)
    except Resolver404:
        return True  # ปล่อยให้ Django ตอบ 404 เอง
    if match.namespace == "accounts":
        return match.url_name in OPEN_ACCOUNT_PAGES
    # URL ของ allauth (SSO callback ฯลฯ) อยู่ใต้ /accounts/ แต่ไม่มี namespace
    return path.startswith("/accounts/") and not match.namespace


class AccessGateMiddleware:
    """
    ทุก request ของผู้ใช้ที่ login แล้ว:
    1. ถูกระงับสิทธิ์ (USER.blocked) → หน้าแจ้งระงับสิทธิ์ แม้จะ login ค้างไว้ก่อนถูกระงับ (UC-15, UC-27, UC-32)
    2. นักศึกษาที่ยังไม่กรอกรหัสนักศึกษา/เบอร์โทร → หน้ากรอกข้อมูลครั้งแรก (UC-15 ข้อ 3ก)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        redirect_to = self._gate(request)
        if redirect_to:
            return redirect(redirect_to)
        return self.get_response(request)

    def _gate(self, request):
        user = request.user
        if not user.is_authenticated or is_exempt(request.path_info):
            return None
        role = get_role(user)
        if role == ADMIN:
            return None
        ubu = get_ubu_user(user)
        if ubu and ubu.blocked:
            return reverse("accounts:blocked")
        if role == STUDENT and not ubu.student.is_profile_complete:
            return reverse("accounts:onboarding")
        return None
