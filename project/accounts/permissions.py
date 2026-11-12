"""
ตัวเช็กสิทธิ์ตามบทบาท ใช้ตัวเดียวทั้งระบบ

    @role_required("student")
    def cart_view(request): ...

    class PendingRequestsView(RoleRequiredMixin, ListView):
        allowed_roles = ("staff",)

ยังไม่ login → ไปหน้า login · login แล้วแต่บทบาทไม่ตรง → 403 (templates/403.html)
"""
from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from .roles import get_role


def _check(request, roles):
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    if get_role(request.user) not in roles:
        raise PermissionDenied("บทบาทของคุณไม่มีสิทธิ์เข้าถึงหน้านี้")
    return None


def role_required(*roles):
    """decorator สำหรับ function view · รับได้หลายบทบาท เช่น role_required("staff", "admin")"""
    if not roles:
        raise ValueError("ต้องระบุบทบาทอย่างน้อย 1 บทบาท")

    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            return _check(request, roles) or view(request, *args, **kwargs)
        return wrapper
    return decorator


class RoleRequiredMixin:
    """mixin สำหรับ class-based view · กำหนด allowed_roles = ("staff",)"""

    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if not self.allowed_roles:
            raise ValueError(f"{type(self).__name__} ต้องกำหนด allowed_roles")
        return _check(request, self.allowed_roles) or super().dispatch(request, *args, **kwargs)
