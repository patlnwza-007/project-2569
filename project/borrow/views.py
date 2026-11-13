"""M3 · borrow รอบ 3a — UC-05 ตะกร้า, UC-06 ส่งคำขอ, UC-07 ยกเลิก, UC-09 หน้าหลัก, แจ้งย้ายที่ตั้ง"""
from datetime import timedelta

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from accounts.navigation import url_ready
from accounts.permissions import role_required
from accounts.roles import STUDENT, get_ubu_user
from catalog.models import Item

from . import services
from .forms import RequestForm
from .models import BorrowItem, BorrowRequest, CartItem, Queue

ACTIVE = (BorrowRequest.Status.PENDING, BorrowRequest.Status.BORROWING, BorrowRequest.Status.RETURN_PENDING)
RECENT_DAYS = 7  # ตัดสินใจ M3 ข้อ 9


def _student(request):
    return get_ubu_user(request.user).student


def _first_error(err):
    return err.messages[0] if err.messages else "เกิดข้อผิดพลาด"


def _back(request, default):
    nxt = request.POST.get("next", "")
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return redirect(nxt)
    return redirect(default)


# ---- UC-05 ตะกร้า ------------------------------------------------------------
@require_POST
@role_required(STUDENT)
def cart_add_view(request, item_id):
    """UC-05 (CartAddView) · มาจาก popup เลือกจำนวนในหน้ารายการ/รายละเอียด"""
    item = get_object_or_404(Item.objects.select_related("material", "durablematerial", "equipment"), pk=item_id)
    try:
        services.cart_add(_student(request), item, request.POST.get("qty", 1))
    except (ValidationError, ValueError) as err:
        messages.error(request, _first_error(err) if isinstance(err, ValidationError) else "จำนวนไม่ถูกต้อง")
    else:
        messages.success(request, f"ใส่ \"{item}\" ลงตะกร้าแล้ว")
    return _back(request, "catalog:item_list")


@role_required(STUDENT)
def cart_view(request):
    """UC-05 (CartDetailView) · ตรวจตัดหน้าทุกครั้งที่เปิดหน้า (Anti-Snipe)"""
    lines = services.cart_lines(_student(request))
    sniped = [line for line, _, s in lines if s]
    types = {line.item.item_type for line, _, _ in lines}
    return render(request, "borrow/cart.html", {
        "lines": lines, "sniped_count": len(sniped), "total_qty": sum(line.qty for line, _, _ in lines),
        "mixed": Item.ItemType.MATERIAL in types and len(types) > 1,
        "queue_ready": url_ready("borrow:queue_join", 0),
    })


@require_POST
@role_required(STUDENT)
def cart_update_view(request, line_id):
    line = get_object_or_404(CartItem.objects.select_related("item"), pk=line_id, cart__student=_student(request))
    try:
        services.cart_update(line, request.POST.get("qty", line.qty))
    except (ValidationError, ValueError) as err:
        messages.error(request, _first_error(err) if isinstance(err, ValidationError) else "จำนวนไม่ถูกต้อง")
    return redirect("borrow:cart")


@require_POST
@role_required(STUDENT)
def cart_remove_view(request, line_id):
    student = _student(request)
    if request.POST.get("all_sniped"):
        removed = [line.pk for line, _, s in services.cart_lines(student) if s]
        CartItem.objects.filter(pk__in=removed).delete()
        messages.success(request, f"ลบรายการที่ไม่พร้อมยืม {len(removed)} รายการแล้ว")
    else:
        CartItem.objects.filter(pk=line_id, cart__student=student).delete()
    return redirect("borrow:cart")


# ---- UC-06 ส่งคำขอ -----------------------------------------------------------
@role_required(STUDENT)
def request_create_view(request):
    """UC-06 (RequestCreateView)"""
    student = _student(request)
    if not student.is_profile_complete:  # UC-06 Alternative → UC-13
        messages.warning(request, "กรุณากรอกเบอร์โทรศัพท์ให้ครบก่อนส่งคำขอยืม")
        return redirect(f"{reverse('accounts:profile')}?next={reverse('borrow:request_create')}")
    lines = services.cart_lines(student)
    if not lines:
        messages.info(request, "ตะกร้าว่าง กรุณาเลือกสิ่งของก่อน")
        return redirect("borrow:cart")
    if any(s for _, _, s in lines):
        messages.error(request, "มีรายการในตะกร้าถูกยืม/เบิกตัดหน้า กรุณาจองคิวแทนหรือลบออกก่อน")
        return redirect("borrow:cart")

    form = RequestForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        photos = {line.pk: request.FILES.get(f"photo_{line.pk}") for line, _, _ in lines}
        try:
            req = services.submit_request(student, form.cleaned_data["is_special"],
                                          form.cleaned_data.get("custom_due_date"), photos)
        except services.SnipedError as err:
            messages.error(request, _first_error(err))
            return redirect("borrow:cart")
        except ValidationError as err:
            if hasattr(err, "error_dict") and "custom_due_date" in err.message_dict:
                form.add_error("custom_due_date", err.message_dict["custom_due_date"])
            else:
                form.add_error(None, err.messages)
        else:
            messages.success(request, f"ส่งคำขอ #{req.pk} แล้ว กรุณานำสิ่งของไปแสดงที่เคาน์เตอร์เพื่อให้เจ้าหน้าที่ตรวจ")
            return redirect("borrow:request_list")
    return render(request, "borrow/request_form.html", {"form": form, "lines": lines})


# ---- UC-09 หน้าหลัก + UC-07 ยกเลิก + แจ้งย้าย -----------------------------------
@role_required(STUDENT)
def request_list_view(request):
    """UC-09 (StudentDashboardView) · คำขอที่ยังไม่จบ + ที่จบภายใน 7 วัน"""
    student = _student(request)
    since = timezone.now() - timedelta(days=RECENT_DAYS)
    items_qs = BorrowItem.objects.select_related("item", "item__equipment", "item__material", "item__durablematerial")
    reqs = (BorrowRequest.objects.filter(student=student)
            .filter(Q(status__in=ACTIVE) | Q(created_at__gte=since))
            .prefetch_related(Prefetch("items", queryset=items_qs), "return_requests__items")
            .order_by("-created_at"))
    today = timezone.localdate()
    cards = []
    for r in reqs:
        items = list(r.items.all())
        types = {bi.item.item_type for bi in items}
        rows = []
        for bi in items:
            rows.append({
                "bi": bi, "days_left": (bi.due_date - today).days if bi.due_date else None,
                "outstanding": bi.qty_outstanding,
                "can_relocate": r.status in services.ACTIVE_LOAN and bi.item.is_returnable and bi.qty_outstanding > 0,
            })
        cards.append({
            "req": r, "rows": rows, "single_type": items[0].item.get_item_type_display() if len(types) == 1 and items else "",
            "fine": r.total_fine, "lost": sum(ri.lost_compensation for rr in r.return_requests.all() for ri in rr.items.all()),
            "can_return": r.status == BorrowRequest.Status.BORROWING and any(row["outstanding"] > 0 for row in rows),
        })
    queues = Queue.objects.filter(student=student, status__in=[Queue.Status.WAITING, Queue.Status.NOTIFIED]) \
        .select_related("item", "item__equipment")
    return render(request, "borrow/request_list.html", {
        "cards": cards, "queues": queues, "has_any": BorrowRequest.objects.filter(student=student).exists(),
        "return_ready": url_ready("borrow:return_notify", 0), "queue_list_ready": url_ready("borrow:queue_list"),
        "history_ready": url_ready("borrow:history"),
    })


@require_POST
@role_required(STUDENT)
def request_cancel_view(request, pk):
    """UC-07 (RequestCancelView)"""
    req = get_object_or_404(BorrowRequest, pk=pk, student=_student(request))
    try:
        services.cancel_request(_student(request), req)
    except ValidationError as err:
        messages.error(request, _first_error(err))
    else:
        messages.success(request, f"ยกเลิกคำขอ #{req.pk} แล้ว สิ่งของถูกคืนเข้าคลัง")
    return redirect("borrow:request_list")


@require_POST
@role_required(STUDENT)
def relocate_view(request, pk):
    """แจ้งย้ายที่ตั้งของที่กำลังยืม (ตัดสินใจ M3 ข้อ 6)"""
    bi = get_object_or_404(BorrowItem.objects.select_related("borrow_request", "item"), pk=pk,
                           borrow_request__student=_student(request))
    try:
        services.relocate(_student(request), bi, request.POST.get("location"))
    except ValidationError as err:
        messages.error(request, _first_error(err))
    else:
        messages.success(request, f"บันทึกที่ตั้งใหม่ของ \"{bi.item}\" แล้ว")
    return redirect("borrow:request_list")
