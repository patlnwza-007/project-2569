"""M3 · borrow รอบ 3a — UC-05 ตะกร้า, UC-06 ส่งคำขอ, UC-07 ยกเลิก, UC-09 หน้าหลัก, แจ้งย้ายที่ตั้ง"""
from datetime import timedelta

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Prefetch, Q
from django.http import Http404
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
            "pending_return": services.pending_return(r) if r.status == BorrowRequest.Status.RETURN_PENDING else None,
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


# =============================================================================
# รอบ 3b — UC-08 แจ้งคืน, UC-10 คิว, UC-11 ประวัติ, UC-38 แจ้งชำรุด
# =============================================================================
from .models import DamageReport, ReturnItem, ReturnRequest  # noqa: E402


@role_required(STUDENT)
def return_notify_view(request, pk):
    """UC-08 (ReturnNotifyView) · ติ๊กเลือกชิ้นที่คืน + สภาพต่อชิ้น + รูปหลักฐาน (บังคับ)"""
    student = _student(request)
    req = get_object_or_404(BorrowRequest, pk=pk, student=student)
    pending = services.pending_return(req)
    lines = services.returnable_lines(req) if not pending else []
    errors = {}
    if request.method == "POST" and not pending:
        selections = []
        for bi, left in lines:
            if request.POST.get(f"pick_{bi.pk}"):
                selections.append((bi.pk, request.POST.get(f"qty_{bi.pk}", left),
                                   request.POST.get(f"cond_{bi.pk}", ""), request.POST.get(f"desc_{bi.pk}", "")))
        try:
            services.notify_return(student, req, selections, request.FILES.get("return_photo"),
                                   request.POST.get("note", ""))
        except (ValidationError, ValueError) as err:
            if isinstance(err, ValidationError) and hasattr(err, "error_dict"):
                errors = {k: v[0] for k, v in err.message_dict.items()}
            else:
                errors = {"__all__": err.messages[0] if isinstance(err, ValidationError) else "จำนวนไม่ถูกต้อง"}
        else:
            messages.success(request, f"แจ้งคืนคำขอ #{req.pk} แล้ว กรุณานำสิ่งของไปแสดงที่เคาน์เตอร์")
            return redirect("borrow:request_list")
    elif request.method == "GET" and req.status != BorrowRequest.Status.BORROWING and not pending:
        messages.error(request, f"แจ้งคืนไม่ได้ เพราะคำขอนี้อยู่ในสถานะ \"{req.get_status_display()}\"")
        return redirect("borrow:request_list")
    return render(request, "borrow/return_notify.html", {
        "req": req, "lines": lines, "pending": pending, "errors": errors, "post": request.POST,
        "conditions": ReturnItem.Condition.choices,
    })


@require_POST
@role_required(STUDENT)
def return_cancel_view(request, pk):
    rr = get_object_or_404(ReturnRequest, pk=pk, borrow_request__student=_student(request))
    try:
        services.cancel_return(_student(request), rr)
    except ValidationError as err:
        messages.error(request, _first_error(err))
    else:
        messages.success(request, "ยกเลิกการแจ้งคืนแล้ว สถานะกลับเป็นกำลังยืม")
    return redirect("borrow:request_list")


@require_POST
@role_required(STUDENT)
def queue_join_view(request, item_id):
    """UC-10 (QueueJoinView) · จากหน้ารายการ/รายละเอียด หรือ "จองคิวแทน" ในตะกร้า"""
    student = _student(request)
    item = get_object_or_404(Item, pk=item_id)
    try:
        q = services.join_queue(student, item)
    except ValidationError as err:
        messages.error(request, _first_error(err))
        return _back(request, "catalog:item_list")
    if request.POST.get("from_cart"):
        CartItem.objects.filter(pk=request.POST["from_cart"], cart__student=student).delete()
    pos = services.queue_position(q)
    date, note = services.estimate_available(q, pos)
    when = f" · คาดว่าจะได้ยืมประมาณ {date:%d/%m/%Y}" if date else ""
    messages.success(request, f"จองคิว \"{q.item}\" แล้ว คุณอยู่ลำดับที่ {pos}{when}")
    return redirect("borrow:queue_list")


@role_required(STUDENT)
def queue_list_view(request):
    """UC-10 (QueueListView) · คิวที่หมดเวลาจะ EXPIRED และเลื่อนคิวถัดไปทุกครั้งที่เปิดหน้า"""
    services.expire_and_advance()
    student = _student(request)
    qs = Queue.objects.filter(student=student).select_related("item", "item__equipment", "item__durablematerial") \
        .order_by("-joined_at")
    active, past = [], []
    for q in qs:
        if q.status in services.ACTIVE_QUEUE + (Queue.Status.CONFIRMED,):
            pos = services.queue_position(q) if q.status != Queue.Status.CONFIRMED else None
            date, note = services.estimate_available(q, pos) if q.status == Queue.Status.WAITING else (None, "")
            active.append({"q": q, "pos": pos, "date": date, "note": note})
        else:
            past.append(q)
    return render(request, "borrow/queue_list.html", {"active": active, "past": past[:20]})


@require_POST
@role_required(STUDENT)
def queue_action_view(request, pk, action):
    if action not in ("confirm", "leave"):
        raise Http404
    q = get_object_or_404(Queue, pk=pk, student=_student(request))
    try:
        if action == "confirm":
            services.confirm_queue(_student(request), q)
            messages.success(request, f"ยืนยันรับสิทธิ์คิว \"{q.item}\" แล้ว กรุณามายืมที่เคาน์เตอร์")
        else:
            services.leave_queue(_student(request), q)
            messages.success(request, f"ออกจากคิว \"{q.item}\" แล้ว")
    except ValidationError as err:
        messages.error(request, _first_error(err))
    return redirect("borrow:queue_list")


@role_required(STUDENT)
def history_view(request):
    """UC-11 (BorrowHistoryListView) · คำขอที่จบแล้ว + สถานะการประเมินรายชิ้น"""
    student = _student(request)
    items_qs = BorrowItem.objects.select_related("item", "item__equipment", "review", "borrow_request")
    status = request.GET.get("status", "")
    reqs = BorrowRequest.objects.filter(student=student, status__in=services.FINISHED) \
        .prefetch_related(Prefetch("items", queryset=items_qs)).order_by("-created_at")
    if status in services.FINISHED:
        reqs = reqs.filter(status=status)
    rows = []
    for r in reqs:
        items = list(r.items.all())
        reviewable = [bi for bi in items if services.is_reviewable(bi)]
        done = [bi for bi in reviewable if hasattr(bi, "review")]
        returned_at = r.return_requests.filter(status=ReturnRequest.Status.RETURNED).order_by("-returned_at") \
            .values_list("returned_at", flat=True).first()
        rows.append({"req": r, "items": items, "reviewable": {bi.pk for bi in reviewable},
                     "reviewed": len(done), "review_total": len(reviewable), "returned_at": returned_at})
    return render(request, "borrow/history.html", {
        "rows": rows, "status": status, "has_any": BorrowRequest.objects.filter(student=student).exists(),
        "status_choices": [(s, BorrowRequest.Status(s).label) for s in services.FINISHED],
        "evaluate_ready": url_ready("evaluation:evaluate"),
    })


@role_required(STUDENT)
def report_damage_view(request):
    """UC-38 (ReportDamageCreateView) · อุปกรณ์ประจำห้อง หรือครุภัณฑ์ในระบบ"""
    student = _student(request)
    errors = {}
    if request.method == "POST":
        try:
            r = services.report_damage(
                student, request.POST.get("kind"), request.POST.get("symptom"), request.POST.get("location"),
                request.POST.get("item_name"), request.POST.get("asset_tag"), request.FILES.get("photo"))
        except ValidationError as err:
            errors = {k: v[0] for k, v in err.message_dict.items()}
        else:
            messages.success(request, f"ส่งเรื่องแจ้งซ่อม #{r.pk} แล้ว เจ้าหน้าที่จะตรวจสอบโดยเร็ว")
            return redirect("borrow:report_damage")
    from catalog.models import Equipment
    return render(request, "borrow/report_damage.html", {
        "errors": errors, "post": request.POST, "kind": request.POST.get("kind", services.ROOM),
        "reports": DamageReport.objects.filter(student=student).select_related("item")[:30],
        "asset_tags": Equipment.objects.exclude(status__in=[Equipment.Status.RETIRED, Equipment.Status.LOST])
                                       .select_related("item").order_by("asset_tag")[:500],
    })
