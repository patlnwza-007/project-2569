from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import AdminLoginForm, FirstTimeSetupForm, ProfilePhoneForm
from .navigation import NAV_BY_KEY, home_url
from .permissions import role_required
from .roles import STUDENT, get_role, get_ubu_user


class CustomLoginView(LoginView):
    """UC-15 — หน้าเข้าสู่ระบบ 2 ช่องทาง

    GET  /accounts/login/            → แท็บ UBU SSO (ปุ่มไป Google ผ่าน allauth)
    GET  /accounts/login/?tab=admin  → แท็บผู้ดูแลระบบ
    POST /accounts/login/admin/      → ตรวจ username/password ของ Django superuser
    """

    template_name = 'accounts/login.html'
    form_class = AdminLoginForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        is_admin = self.request.method == 'POST' or self.request.GET.get('tab') == 'admin'
        ctx['active_tab'] = 'admin' if is_admin else 'sso'
        return ctx

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


def _safe_next(request):
    nxt = request.POST.get('next') or request.GET.get('next')
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return nxt
    return None


@login_required
def first_time_setup_view(request):
    """UC-15 ข้อ 3ก (FirstTimeSetupView): บันทึกรหัสนักศึกษา 11 หลัก + เบอร์โทร 10 หลัก ก่อนเข้าใช้งาน"""
    ubu = get_ubu_user(request.user)
    if not ubu or not ubu.is_student or ubu.student.is_profile_complete:
        return redirect('home')
    student = ubu.student
    form = FirstTimeSetupForm(
        request.POST or None, student=student,
        initial={'name': ubu.name, 'student_id': student.student_id or '', 'phone': student.phone},
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'บันทึกข้อมูลเรียบร้อย ยินดีต้อนรับสู่ YuemDee')
        return redirect('home')
    return render(request, 'accounts/onboarding.html', {'form': form, 'ubu_user': ubu})


@role_required(STUDENT)
def profile_view(request):
    """UC-13 (ProfileDetailView / ProfileUpdateView): โหมดดูเป็นค่าเริ่มต้น · ?edit=1 = โหมดแก้ไขเบอร์โทร

    มาจาก UC-06 ด้วย ?next=<url> → เปิดโหมดแก้ไข แสดงแถบเตือน และบันทึกแล้วพากลับไปหน้าเดิม
    """
    ubu = get_ubu_user(request.user)
    student = ubu.student
    nxt = _safe_next(request)
    edit_mode = request.method == 'POST' or request.GET.get('edit') == '1' or bool(nxt)

    form = ProfilePhoneForm(request.POST or None, instance=student)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'บันทึกข้อมูลส่วนตัวสำเร็จ')
        return redirect(nxt or reverse('accounts:profile'))

    return render(request, 'accounts/profile.html', {
        'ubu_user': ubu, 'student': student, 'form': form,
        'edit_mode': edit_mode, 'next': nxt,
    })
