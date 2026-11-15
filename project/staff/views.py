"""M6 · staff รอบ 6a — UC-16 แดชบอร์ด, UC-17 ปล่อยของ, UC-18 รับคืน, UC-36 ค่าปรับ"""
from datetime import date

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Prefetch, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from accounts.navigation import url_ready
from accounts.permissions import role_required
from accounts.roles import STAFF, get_ubu_user
from borrow import services as borrow
from borrow.models import BorrowItem, BorrowRequest, DamageReport, ReturnItem, ReturnRequest
from catalog.models import Equipment
from suggestion.models import Suggestion

from . import services

S = BorrowRequest.Status
ITEMS = BorrowItem.objects.select_related("item", "item__equipment", "item__material", "item__durablematerial")
TABS = [("all", "ทั้งหมด"), ("pending", "รอตรวจรับคืน"), ("overdue", "เกินกำหนด"), ("partial", "คืนบางส่วน"),
        ("unpaid", "ค้างชำระ")]


def _staff(request):
    return get_ubu_user(request.user).staff


def _err(err):
    return err.messages[0] if err.messages else "เกิดข้อผิดพลาด"


def _back(request, default):
    nxt = request.POST.get("next", "")
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return redirect(nxt)
    return redirect(default)


def _overdue_items(today):
    """รายการที่ยังคืนไม่ครบและเลยกำหนดคืน"""
    qs = ITEMS.filter(borrow_request__status__in=[S.BORROWING, S.RETURN_PENDING], due_date__lt=today)
    return [bi for bi in qs if bi.qty_outstanding > 0]


# ---- UC-16 ------------------------------------------------------------------
@role_required(STAFF)
def dashboard_view(request):
    """UC-16 (StaffDashboardView) · การ์ด 6 ใบ + คำขอรอตรวจล่าสุด (ตัดสินใจ M6 ข้อ 9)"""
    borrow.expire_and_advance()
    today = timezone.localdate()
    cards = [
        ("⏳", "รอตรวจของหน้าเคาน์เตอร์", BorrowRequest.objects.filter(status=S.PENDING).count(), "staff:pending_requests", "amber"),
        ("📦", "กำลังยืมอยู่", BorrowRequest.objects.filter(status=S.BORROWING).count(), "staff:return_list", "blue"),
        ("↩️", "รอตรวจรับคืน", ReturnRequest.objects.filter(status=ReturnRequest.Status.RETURN_PENDING).count(), "staff:return_list", "purple"),
        ("🔴", "เกินกำหนดคืน", len(_overdue_items(today)), "staff:return_list", "red"),
        ("⚠️", "ครุภัณฑ์เสียหาย / แจ้งซ่อม",
         Equipment.objects.filter(status=Equipment.Status.DAMAGED).count()
         + DamageReport.objects.filter(status=DamageReport.Status.PENDING).count(), "staff:damaged_equipment", "orange"),
        ("💡", "คำเสนอแนะรอพิจารณา", Suggestion.objects.filter(status=Suggestion.Status.SUBMITTED).count(), "suggestion:review", "teal"),
    ]
    tab_for = {"↩️": "?tab=pending", "🔴": "?tab=overdue"}
    cards = [{"icon": i, "label": l, "count": c, "url": n if url_ready(n) else "", "suffix": tab_for.get(i, ""),
              "color": col} for i, l, c, n, col in cards]
    latest = BorrowRequest.objects.filter(status=S.PENDING).select_related("student__user") \
        .prefetch_related(Prefetch("items", queryset=ITEMS)).order_by("created_at")[:10]
    return render(request, "staff/dashboard.html", {"cards": cards, "latest": latest})


# ---- UC-17 ------------------------------------------------------------------
@role_required(STAFF)
def pending_requests_view(request):
    """UC-17 (RequestApproveRejectView) · ตรวจนับของจริงบนโต๊ะ ติ๊กรายชิ้น"""
    q = request.GET.get("q", "").strip()
    reqs = BorrowRequest.objects.filter(status=S.PENDING).select_related("student__user") \
        .prefetch_related(Prefetch("items", queryset=ITEMS)).order_by("created_at")
    if q:
        reqs = reqs.filter(_search(q)).distinct()
    return render(request, "staff/pending_requests.html", {"reqs": reqs, "q": q, "today": timezone.localdate()})


@require_POST
@role_required(STAFF)
def request_approve_view(request, pk):
    req = get_object_or_404(BorrowRequest, pk=pk)
    due = request.POST.get("custom_due_date") or None
    try:
        due = date.fromisoformat(due) if due else None
        req, removed = services.approve_request(_staff(request), req, request.POST.getlist("keep"), due)
    except (ValidationError, ValueError) as err:
        messages.error(request, f"คำขอ #{pk}: " + (_err(err) if isinstance(err, ValidationError) else "วันที่ไม่ถูกต้อง"))
    else:
        extra = f" · ตัดออก {len(removed)} รายการ (คืนเข้าคลังแล้ว)" if removed else ""
        messages.success(request, f"ปล่อยของคำขอ #{pk} แล้ว — {req.get_status_display()}{extra}")
    return redirect("staff:pending_requests")


@require_POST
@role_required(STAFF)
def request_reject_view(request, pk):
    req = get_object_or_404(BorrowRequest, pk=pk)
    try:
        services.reject_request(_staff(request), req, request.POST.get("reject_reason"))
    except ValidationError as err:
        messages.error(request, f"คำขอ #{pk}: {_err(err)}")
    else:
        messages.success(request, f"ปฏิเสธคำขอ #{pk} แล้ว สิ่งของถูกคืนเข้าคลัง")
    return redirect("staff:pending_requests")


# ---- UC-18 + UC-36 ----------------------------------------------------------
@role_required(STAFF)
def return_list_view(request):
    """UC-18 (ReturnConfirmView) + UC-36 · แท็บ ทั้งหมด/รอตรวจรับคืน/เกินกำหนด/คืนบางส่วน/ค้างชำระ"""
    borrow.expire_and_advance()
    tab = request.GET.get("tab", "pending" if ReturnRequest.objects.filter(
        status=ReturnRequest.Status.RETURN_PENDING).exists() else "all")
    q = request.GET.get("q", "").strip()
    today = timezone.localdate()
    ctx = {"tab": tab, "tabs": TABS, "q": q, "today": today}

    if tab == "unpaid":  # ตัดสินใจ M6 ข้อ 8
        rrs = ReturnRequest.objects.filter(status=ReturnRequest.Status.RETURNED) \
            .select_related("borrow_request__student__user", "inspected_by__user") \
            .prefetch_related(Prefetch("items", queryset=ReturnItem.objects.select_related("borrow_item__item__equipment"))) \
            .order_by("-returned_at")
        if q:
            rrs = rrs.filter(_search(q, "borrow_request__"))
        ctx["unpaid"] = [rr for rr in rrs if services.has_unpaid(rr)]
        return render(request, "staff/return_list.html", ctx)

    reqs = BorrowRequest.objects.filter(status__in=[S.BORROWING, S.RETURN_PENDING]) \
        .select_related("student__user").prefetch_related(Prefetch("items", queryset=ITEMS)).order_by("created_at")
    if q:
        reqs = reqs.filter(_search(q)).distinct()
    if tab == "pending":
        reqs = reqs.filter(status=S.RETURN_PENDING)
    cards = []
    for r in reqs:
        lines, pending = services.outstanding_lines(r)
        if not lines:
            continue
        overdue = any(bi.due_date and bi.due_date < today for bi, _, _ in lines)
        partial = any(bi.qty_returned for bi in r.items.all())
        if (tab == "overdue" and not overdue) or (tab == "partial" and not partial):
            continue
        rows = [{"bi": bi, "left": left, "declared": d,
                 "fine_preview": borrow.compute_fine(bi, today, left),
                 "late_days": max(0, (today - bi.due_date).days) if bi.due_date else 0} for bi, left, d in lines]
        cards.append({"req": r, "pending": pending, "rows": rows, "overdue": overdue, "partial": partial,
                      "returned": sum(bi.qty_returned for bi in r.items.all() if bi.item.is_returnable),
                      "total": sum(bi.qty for bi in r.items.all() if bi.item.is_returnable)})
    ctx["cards"] = cards
    ctx["conditions"] = ReturnItem.Condition.choices
    return render(request, "staff/return_list.html", ctx)


def _search(q, prefix=""):
    cond = Q(**{f"{prefix}student__user__name__icontains": q}) | Q(**{f"{prefix}student__student_id__icontains": q}) \
        | Q(**{f"{prefix}items__item__equipment__asset_tag__icontains": q})
    if q.isdigit():
        cond |= Q(**{f"{prefix}pk": int(q)} if prefix else {"pk": int(q)})
    return cond


@require_POST
@role_required(STAFF)
def return_confirm_view(request, pk):
    """UC-18: ยืนยันรับคืน (มีหรือไม่มีการแจ้งคืนจากนักศึกษาก็ได้ — ตัดสินใจ M6 ข้อ 3)"""
    req = get_object_or_404(BorrowRequest, pk=pk)
    rows = []
    for bi_id in request.POST.getlist("receive"):
        rows.append((bi_id, request.POST.get(f"qty_{bi_id}", 1), request.POST.get(f"cond_{bi_id}", ""),
                     request.POST.get(f"lost_{bi_id}"), request.POST.get(f"note_{bi_id}", "")))
    try:
        rr, now_qty, left = services.confirm_return(
            _staff(request), req, rows, request.POST.get("custom_fine"), request.POST.get("fine_reason"),
            request.POST.get("fine_paid") == "on")
    except (ValidationError, ValueError) as err:
        messages.error(request, f"คำขอ #{pk}: " + (_err(err) if isinstance(err, ValidationError) else "ข้อมูลไม่ถูกต้อง"))
    else:
        tail = f" (ยังค้างส่งอีก {left} ชิ้น)" if left else " — คืนครบแล้ว"
        fine = f" · ค่าปรับ ฿{rr.total_fine:,.2f}" if rr.total_fine else ""
        messages.success(request, f"รับคืนคำขอ #{pk} แล้ว {now_qty} ชิ้น{tail}{fine}")
    return _back(request, "staff:return_list")


@require_POST
@role_required(STAFF)
def edit_fine_view(request, pk):
    """UC-36 (FineManagementView): แก้ยอดค่าปรับ / สลับสถานะชำระ / ค่าชดใช้ของหาย"""
    rr = get_object_or_404(ReturnRequest, pk=pk, status=ReturnRequest.Status.RETURNED)
    action = request.POST.get("action")
    try:
        if action == "fine":
            services.update_fine(rr, request.POST.get("custom_fine"), request.POST.get("fine_reason"))
            messages.success(request, f"บันทึกยอดค่าปรับรอบคืน #{rr.pk} แล้ว")
        elif action == "fine_paid":
            services.set_fine_paid(rr, request.POST.get("paid") == "1")
            messages.success(request, f"บันทึกสถานะชำระค่าปรับรอบคืน #{rr.pk} แล้ว")
        elif action == "lost":
            ri = get_object_or_404(ReturnItem, pk=request.POST.get("item"), return_request=rr)
            services.update_lost(ri, request.POST.get("lost_compensation"),
                                 request.POST.get("paid") == "1" if "paid" in request.POST else None)
            messages.success(request, "บันทึกค่าชดใช้แล้ว")
        else:
            raise Http404
    except ValidationError as err:
        messages.error(request, _err(err))
    return _back(request, "staff:return_list")
