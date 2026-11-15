"""
M6 · staff รอบ 6a — UC-17 ปล่อยของ/ปฏิเสธ · UC-18 ตรวจรับคืน · UC-36 ค่าปรับ
ข้อตัดสินใจ: docs/generated_mapping/M6_staff.md หัวข้อ 9
"""
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from borrow import services as borrow
from borrow.models import BorrowItem, BorrowRequest, ReturnItem, ReturnRequest
from catalog.models import DurableMaterial, Equipment

S = BorrowRequest.Status
C = ReturnItem.Condition
WALK_IN_NOTE = "รับคืนที่เคาน์เตอร์ (นักศึกษาไม่ได้แจ้งคืนในระบบ)"


def _money(value, field):
    if value in (None, ""):
        return None
    try:
        d = Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        raise ValidationError({field: "กรุณากรอกจำนวนเงินเป็นตัวเลข"})
    if d < 0:
        raise ValidationError({field: "จำนวนเงินต้องไม่ติดลบ"})
    return d


# ---- UC-17 ปล่อยของ / ปฏิเสธ --------------------------------------------------
@transaction.atomic
def approve_request(staff, borrow_request, keep_ids, custom_due_date=None):
    """UC-17: ปล่อยของเฉพาะชิ้นที่ติ๊ก · ชิ้นที่ติ๊กออก → ลบ + คืนของที่จองไว้ (ตัดสินใจ M6 ข้อ 2)"""
    req = BorrowRequest.objects.select_for_update().get(pk=borrow_request.pk)
    if req.status != S.PENDING:
        raise ValidationError(f"ปล่อยของไม่ได้ เพราะคำขอนี้อยู่ในสถานะ \"{req.get_status_display()}\" แล้ว")
    keep_ids = {int(i) for i in keep_ids}
    items = list(req.items.select_related("item", "item__equipment", "item__material", "item__durablematerial"))
    kept = [bi for bi in items if bi.pk in keep_ids]
    if not kept:
        raise ValidationError("ไม่ได้เลือกสิ่งของที่จะปล่อยเลย หากไม่ปล่อยของ ให้กด \"ปฏิเสธคำขอ\" แทน")
    removed = [bi for bi in items if bi.pk not in keep_ids]
    if removed:
        borrow.release_stock_items(removed)
        BorrowItem.objects.filter(pk__in=[bi.pk for bi in removed]).delete()
    if req.is_special:
        if custom_due_date:
            if custom_due_date <= timezone.localdate():
                raise ValidationError({"custom_due_date": "วันที่อนุญาตคืนต้องเป็นวันในอนาคต"})
            req.custom_due_date = custom_due_date
        elif not req.custom_due_date:
            raise ValidationError({"custom_due_date": "คำขอกรณีพิเศษต้องระบุวันที่อนุญาตคืน"})
    today = timezone.localdate()
    for bi in kept:
        bi.borrow_request = req
        bi.due_date = borrow.compute_due_date(bi, today)
        bi.save(update_fields=["due_date"])
    req.status = S.BORROWING if any(bi.item.is_returnable for bi in kept) else S.ISSUED
    req.approved_by = staff
    req.approved_at = timezone.now()
    req.save(update_fields=["status", "approved_by", "approved_at", "custom_due_date"])
    return req, removed


@transaction.atomic
def reject_request(staff, borrow_request, reason):
    """UC-17: ปฏิเสธพร้อมเหตุผล (บังคับ) → คืนของที่จองไว้ทั้งหมด"""
    reason = (reason or "").strip()
    if not reason:
        raise ValidationError({"reject_reason": "กรุณาระบุเหตุผลที่ไม่อนุมัติ"})
    req = BorrowRequest.objects.select_for_update().get(pk=borrow_request.pk)
    if req.status != S.PENDING:
        raise ValidationError(f"ปฏิเสธไม่ได้ เพราะคำขอนี้อยู่ในสถานะ \"{req.get_status_display()}\" แล้ว")
    borrow.release_stock(req)
    req.status = S.REJECTED
    req.reject_reason = reason
    req.approved_by = staff
    req.approved_at = timezone.now()
    req.save(update_fields=["status", "reject_reason", "approved_by", "approved_at"])
    return req


# ---- UC-18 ตรวจรับคืน + UC-36 ค่าปรับ -----------------------------------------
def outstanding_lines(borrow_request):
    """ของที่ยังไม่คืน + สิ่งที่นักศึกษาแจ้งไว้ (ถ้ามี): [(bi, outstanding, declared ReturnItem|None)]"""
    pending = borrow.pending_return(borrow_request)
    declared = {ri.borrow_item_id: ri for ri in pending.items.all()} if pending else {}
    return [(bi, left, declared.get(bi.pk)) for bi, left in borrow.returnable_lines(borrow_request)], pending


@transaction.atomic
def confirm_return(staff, borrow_request, rows, custom_fine=None, fine_reason="", fine_paid=False, today=None):
    """UC-18: ยืนยันรับคืน

    rows = [(borrow_item_id, qty, condition, lost_compensation, note)]
    ไม่มีการแจ้งคืนจากนักศึกษา → สร้าง RETURN_REQUEST ให้ (ตัดสินใจ M6 ข้อ 3)
    """
    today = today or timezone.localdate()
    req = BorrowRequest.objects.select_for_update().get(pk=borrow_request.pk)
    if req.status not in (S.BORROWING, S.RETURN_PENDING):
        raise ValidationError(f"รับคืนไม่ได้ เพราะคำขอนี้อยู่ในสถานะ \"{req.get_status_display()}\"")
    if not rows:
        raise ValidationError("กรุณาเลือกสิ่งของที่รับคืนอย่างน้อย 1 รายการ")
    custom_fine = _money(custom_fine, "custom_fine")
    lines, pending = outstanding_lines(req)
    outstanding = {bi.pk: (bi, left) for bi, left, _ in lines}

    rr = pending or ReturnRequest.objects.create(borrow_request=req, status=ReturnRequest.Status.RETURN_PENDING,
                                                 note=WALK_IN_NOTE)
    declared_ids = set(rr.items.values_list("borrow_item_id", flat=True))
    rr.items.all().delete()

    received, notify_items, equipment_notes = set(), [], []
    for bi_id, qty, condition, lost_comp, note in rows:
        bi_id = int(bi_id)
        if bi_id not in outstanding:
            raise ValidationError("มีรายการที่รับคืนไม่ได้ (คืนครบแล้ว หรือไม่ใช่ของในคำขอนี้)")
        bi, left = outstanding[bi_id]
        qty = int(qty)
        if qty < 1 or qty > left:
            raise ValidationError(f"\"{bi.item}\" รับคืนได้ 1–{left} {bi.item.unit}")
        if condition not in C.values:
            raise ValidationError(f"กรุณาเลือกผลตรวจสภาพของ \"{bi.item}\"")
        item = bi.item
        comp = Decimal("0.00")
        if condition == C.LOST:
            comp = _money(lost_comp, "lost_compensation")
            if comp is None:  # ค่าเริ่มต้นจากราคาจัดซื้อ (UC-18 ข้อ 3)
                comp = (item.purchase_price * qty).quantize(Decimal("0.01"))
        ReturnItem.objects.create(
            return_request=rr, borrow_item=bi, qty_returned=qty, condition_status=condition,
            fine=borrow.compute_fine(bi, today, qty), lost_compensation=comp,
        )
        received.add(bi_id)
        note = (note or "").strip()
        if item.is_equipment:
            new = {C.NORMAL: Equipment.Status.AVAILABLE, C.DAMAGED: Equipment.Status.DAMAGED,
                   C.LOST: Equipment.Status.LOST}[condition]
            eq = Equipment.objects.select_for_update().get(pk=item.pk)
            eq.status = new
            if condition == C.DAMAGED and note:
                eq.note = note  # ตัดสินใจ M6 ข้อ 5
            eq.save(update_fields=["status", "note"])
            if condition == C.NORMAL:
                notify_items.append(item)
        else:
            d = DurableMaterial.objects.select_for_update().get(pk=item.pk)
            if condition == C.NORMAL:
                d.qty_available = min(d.qty_total, d.qty_available + qty)
                notify_items.append(item)
            else:  # ชำรุด (ตัดสินใจ M6 ข้อ 4) / สูญหาย → ตัดออกจากจำนวนทั้งหมด
                d.qty_total = max(d.qty_available, d.qty_total - qty)
            d.save(update_fields=["qty_available", "qty_total"])
        if note and condition != C.NORMAL:
            equipment_notes.append(f"[เจ้าหน้าที่] {item}: {note}")

    # ชิ้นที่นักศึกษาแจ้งคืนแต่ไม่ได้นำมาจริง → กลับเป็นกำลังยืม
    for bi_id in declared_ids - received:
        bi = outstanding.get(bi_id, (None, 0))[0]
        if bi and bi.item.is_equipment:
            Equipment.objects.filter(pk=bi.item_id, status=Equipment.Status.RETURN_PENDING) \
                .update(status=Equipment.Status.BORROWED)

    rr.status = ReturnRequest.Status.RETURNED
    rr.inspected_by = staff
    rr.returned_at = timezone.now()
    rr.custom_fine = custom_fine
    rr.fine_reason = (fine_reason or "").strip()
    rr.fine_paid = bool(fine_paid)
    if equipment_notes:
        rr.note = "\n".join(filter(None, [rr.note, *equipment_notes]))
    rr.save()

    left_after = sum(left for _, left in borrow.returnable_lines(req))
    req.status = S.BORROWING if left_after else S.RETURNED
    req.save(update_fields=["status"])
    for item in notify_items:  # คืนสภาพปกติ → แจ้งคิวถัดไป
        borrow.notify_next(item)
    returned_now = sum(int(r[1]) for r in rows)
    return rr, returned_now, left_after


def update_fine(return_request, custom_fine, fine_reason=""):
    """UC-36: แก้ยอดค่าปรับที่เก็บจริง (ว่าง = ใช้ผลรวมอัตโนมัติ, 0 = ยกเว้น)"""
    return_request.custom_fine = _money(custom_fine, "custom_fine")
    return_request.fine_reason = (fine_reason or "").strip()
    return_request.save(update_fields=["custom_fine", "fine_reason"])


def set_fine_paid(return_request, paid):
    return_request.fine_paid = bool(paid)
    return_request.save(update_fields=["fine_paid"])


def update_lost(return_item, compensation=None, paid=None):
    if compensation is not None:
        value = _money(compensation, "lost_compensation")
        return_item.lost_compensation = value if value is not None else Decimal("0.00")
    if paid is not None:
        return_item.lost_paid = bool(paid)
    return_item.save(update_fields=["lost_compensation", "lost_paid"])


def has_unpaid(return_request):
    if return_request.total_fine > 0 and not return_request.fine_paid:
        return True
    return return_request.items.filter(lost_compensation__gt=0, lost_paid=False).exists()


# =============================================================================
# รอบ 6b · UC-35 ครุภัณฑ์เสียหายและเรื่องแจ้งซ่อม
# =============================================================================
from borrow.models import DamageReport  # noqa: E402
from staff_inventory import services as inventory  # noqa: E402

DAMAGE_STATUSES = (Equipment.Status.DAMAGED, Equipment.Status.MAINTENANCE, Equipment.Status.RETIRED)
REPAIR_ACTIONS = {  # ปุ่มในแท็บ 1 → สถานะใหม่
    "repair": Equipment.Status.MAINTENANCE,  # 🔧 ส่งซ่อม
    "fixed": Equipment.Status.AVAILABLE,     # ✅ ซ่อมเสร็จแล้ว (กลับมาพร้อมให้ยืม + แจ้งคิว)
    "retire": Equipment.Status.RETIRED,      # 📦 ปลดระวาง (ไม่ต้องระบุเหตุผล)
}


@transaction.atomic
def damaged_action(items, action):
    """UC-35 แท็บ 1: เดี่ยวหรือกลุ่ม · ทำได้เฉพาะครุภัณฑ์ที่อยู่ในรายการเสียหาย/ซ่อม/ปลดระวาง"""
    if action not in REPAIR_ACTIONS:
        raise ValidationError("คำสั่งไม่ถูกต้อง")
    status = REPAIR_ACTIONS[action]
    done, skipped = [], []
    for item in items:
        if not item.is_equipment or item.equipment.status not in DAMAGE_STATUSES or item.equipment.status == status:
            skipped.append(item)
            continue
        inventory.change_status(item, status)
        done.append(item)
    return done, skipped


REPORT_FLOW = {"accept": DamageReport.Status.IN_PROGRESS, "close": DamageReport.Status.RESOLVED}


def damage_report_action(report, action):
    """UC-35 แท็บ 2: รับเรื่อง (PENDING → IN_PROGRESS) · ปิดงานซ่อม (→ RESOLVED)"""
    if action not in REPORT_FLOW:
        raise ValidationError("คำสั่งไม่ถูกต้อง")
    if report.status == DamageReport.Status.RESOLVED:
        raise ValidationError("เรื่องนี้ปิดงานไปแล้ว")
    if action == "accept" and report.status != DamageReport.Status.PENDING:
        raise ValidationError("รับเรื่องนี้ไปแล้ว")
    report.status = REPORT_FLOW[action]
    report.save(update_fields=["status"])
