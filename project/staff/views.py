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
from accounts.roles import ADMIN, STAFF, get_ubu_user
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


# =============================================================================
# รอบ 6b — UC-35 ครุภัณฑ์เสียหาย, UC-19 ประวัติทั้งระบบ
# =============================================================================
from django.core.paginator import Paginator  # noqa: E402

from catalog.models import Item  # noqa: E402

DAMAGE_FILTERS = [("", "ทั้งหมด"), ("DAMAGED", "รอส่งซ่อม"), ("MAINTENANCE", "กำลังส่งซ่อม"), ("RETIRED", "ปลดระวาง")]


@role_required(STAFF)
def damaged_equipment_view(request):
    """UC-35 (DamagedEquipmentListView) · แท็บ 1 ครุภัณฑ์เสียหายในคลัง · แท็บ 2 แจ้งซ่อมจากนักศึกษา"""
    tab = request.GET.get("tab", "warehouse")
    ctx = {"tab": tab, "filters": DAMAGE_FILTERS}
    if tab == "reports":
        status = request.GET.get("status", "")
        reports = DamageReport.objects.select_related("student__user", "item__equipment").order_by("-created_at")
        if status in DamageReport.Status.values:
            reports = reports.filter(status=status)
        ctx.update({"reports": reports, "status": status, "report_statuses": DamageReport.Status.choices})
    else:
        f = request.GET.get("f", "")
        items = Item.objects.filter(item_type=Item.ItemType.EQUIPMENT,
                                    equipment__status__in=services.DAMAGE_STATUSES).select_related("equipment") \
            .order_by("equipment__status", "equipment__asset_tag")
        if f in dict(DAMAGE_FILTERS) and f:
            items = items.filter(equipment__status=f)
        ctx.update({"items": items, "f": f})
    ctx["counts"] = {
        "warehouse": Equipment.objects.filter(status__in=services.DAMAGE_STATUSES[:2]).count(),
        "reports": DamageReport.objects.exclude(status=DamageReport.Status.RESOLVED).count(),
    }
    return render(request, "staff/damaged_equipment.html", ctx)


@require_POST
@role_required(STAFF)
def damaged_action_view(request):
    """UC-35 แท็บ 1: ส่งซ่อม / ซ่อมเสร็จ / ปลดระวาง — รายชิ้น (ids=1 ตัว) หรือกลุ่ม"""
    try:
        ids = [int(x) for x in request.POST.get("ids", "").split(",") if x.strip()]
    except ValueError:
        ids = []
    action = request.POST.get("action", "")
    labels = {"repair": "ส่งซ่อม", "fixed": "ซ่อมเสร็จ (พร้อมให้ยืม)", "retire": "ปลดระวาง"}
    if not ids:
        messages.error(request, "กรุณาเลือกครุภัณฑ์อย่างน้อย 1 ชิ้น")
    else:
        try:
            done, skipped = services.damaged_action(
                Item.objects.filter(pk__in=ids).select_related("equipment"), action)
        except ValidationError as err:
            messages.error(request, _err(err))
        else:
            msg = f"{labels.get(action, action)} แล้ว {len(done)} ชิ้น"
            if skipped:
                msg += f" · ข้าม {len(skipped)} ชิ้น (สถานะไม่ตรง)"
            (messages.warning if skipped else messages.success)(request, msg)
    return _back(request, "staff:damaged_equipment")


@require_POST
@role_required(STAFF)
def damage_report_action_view(request, pk, action):
    """UC-35 แท็บ 2: รับเรื่อง / ปิดงานซ่อม"""
    report = get_object_or_404(DamageReport, pk=pk)
    try:
        services.damage_report_action(report, action)
    except ValidationError as err:
        messages.error(request, _err(err))
    else:
        messages.success(request, f"เรื่องแจ้งซ่อม #{pk}: {report.get_status_display()}")
    return _back(request, "staff:damaged_equipment")


@role_required(STAFF, ADMIN)  # แอดมินดูได้ด้วย (ผู้ใช้เลือก 2026-11-16)
def all_history_view(request):
    """UC-19 (StaffHistoryAllView) · แท็บตามคำขอ / แท็บติดตามรายชิ้น · ค้นหา + กรองสถานะ + ช่วงวันที่"""
    tab = request.GET.get("tab", "requests")
    q, status = request.GET.get("q", "").strip(), request.GET.get("status", "")
    d_from, d_to = request.GET.get("from", ""), request.GET.get("to", "")
    keep = request.GET.copy()
    keep.pop("page", None)
    ctx = {"tab": tab, "q": q, "status": status, "from": d_from, "to": d_to, "page_query": keep.urlencode(),
           "today": timezone.localdate()}
    if tab == "units":
        units = Item.objects.filter(item_type=Item.ItemType.EQUIPMENT).select_related("equipment") \
            .order_by("equipment__asset_tag")
        if q:
            units = units.filter(Q(name__icontains=q) | Q(equipment__asset_tag__icontains=q)
                                 | Q(borrow_items__borrow_request__student__user__name__icontains=q)
                                 | Q(borrow_items__borrow_request__student__student_id__icontains=q)).distinct()
        if status in Equipment.Status.values:
            units = units.filter(equipment__status=status)
        page = Paginator(units, 30).get_page(request.GET.get("page"))
        rows = []
        for item in page:
            loan = borrow.current_loan(item) if item.equipment.status in (
                Equipment.Status.BORROWED, Equipment.Status.RETURN_PENDING) else None
            if loan is None and item.equipment.status in (Equipment.Status.BORROWED, Equipment.Status.RETURN_PENDING):
                loan = ITEMS.filter(item=item, borrow_request__status__in=[S.PENDING, S.BORROWING, S.RETURN_PENDING]) \
                    .select_related("borrow_request__student__user").order_by("-borrow_request__created_at").first()
            rows.append({"item": item, "loan": loan})
        ctx.update({"page": page, "rows": rows, "statuses": Equipment.Status.choices})
    else:
        reqs = BorrowRequest.objects.select_related("student__user") \
            .prefetch_related(Prefetch("items", queryset=ITEMS)).order_by("-created_at")
        if q:
            reqs = reqs.filter(_search(q)).distinct()
        if status in S.values:
            reqs = reqs.filter(status=status)
        try:
            if d_from:
                reqs = reqs.filter(created_at__date__gte=date.fromisoformat(d_from))
            if d_to:
                reqs = reqs.filter(created_at__date__lte=date.fromisoformat(d_to))
        except ValueError:
            messages.error(request, "รูปแบบวันที่ไม่ถูกต้อง")
        ctx.update({"page": Paginator(reqs, 30).get_page(request.GET.get("page")), "statuses": S.choices})
    return render(request, "staff/all_history.html", ctx)


@role_required(STAFF, ADMIN)  # แอดมินดูได้ด้วย (ผู้ใช้เลือก 2026-11-16)
def history_detail_view(request, pk):
    """UC-19 (StaffHistoryDetailModalView) · รายละเอียดเจาะลึกของคำขอ"""
    req = get_object_or_404(BorrowRequest.objects.select_related("student__user", "approved_by__user"), pk=pk)
    items = list(ITEMS.filter(borrow_request=req))
    rounds = req.return_requests.select_related("inspected_by__user") \
        .prefetch_related(Prefetch("items", queryset=ReturnItem.objects.select_related("borrow_item__item__equipment"))) \
        .order_by("created_at")
    return render(request, "staff/history_detail.html", {"req": req, "items": items, "rounds": rounds})
