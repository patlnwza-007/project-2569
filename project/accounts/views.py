from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .navigation import NAV_BY_KEY, home_url
from .roles import get_role, get_ubu_user


class CustomLoginView(LoginView):
    """UC-15 — หน้าเข้าสู่ระบบ (ปุ่ม UBU SSO) · ช่องทาง Admin จะเพิ่มตอนทำ M1"""

    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def home_view(request):
    """UC-15 ข้อ 5: นำเข้าหน้าหลักตามบทบาท (นศ. → หน้าคำขอ, จนท. → แดชบอร์ด, แอดมิน → จัดการผู้ใช้)"""
    role = get_role(request.user)
    if role is None:
        raise PermissionDenied("บัญชีนี้ยังไม่มีบทบาทในระบบ กรุณาติดต่อผู้ดูแลระบบ")
    return redirect(home_url(role))


@login_required
def coming_soon_view(request, key):
    """หน้าชั่วคราวของเมนูที่ยังไม่ได้ทำ (เฟส 3 จะแทนด้วยหน้าจริงทีละ module)"""
    if key not in NAV_BY_KEY:
        raise Http404
    role, item = NAV_BY_KEY[key]
    if get_role(request.user) != role:
        raise PermissionDenied("บทบาทของคุณไม่มีสิทธิ์เข้าถึงหน้านี้")
    return render(request, 'coming_soon.html', {'page_item': item})


@login_required
def blocked_view(request):
    """UC-15 Alternative Flow: บัญชีถูกระงับสิทธิ์"""
    ubu = get_ubu_user(request.user)
    if not ubu or not ubu.blocked:
        return redirect('home')
    return render(request, 'accounts/blocked.html', {'ubu_user': ubu})


@login_required
def onboarding_view(request):
    """UC-15 ข้อ 3ก: กรอกรหัสนักศึกษาและเบอร์โทรครั้งแรก — ฟอร์มจริงจะทำตอน M1"""
    ubu = get_ubu_user(request.user)
    if not ubu or not ubu.is_student or ubu.student.is_profile_complete:
        return redirect('home')
    return render(request, 'accounts/onboarding.html')
